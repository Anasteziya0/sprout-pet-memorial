import io
import logging
import os
from html import escape
from pathlib import Path

from rest_framework import generics, permissions, views, status
from rest_framework.response import Response
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from .models import CapsuleCalculation, Pet, TreeSpecies
from .degradation import degradation_breakdown
from .serializers import (
    CalculationRequestSerializer,
    CalculationSerializer,
    PetSerializer,
    TreeSpeciesSerializer,
)
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

logger = logging.getLogger(__name__)


def _matching_tree_species(climate, soil, care_preference, growth_preference):
    climate = climate.strip().casefold()
    soil = soil.strip().casefold()
    candidates = []
    for tree in TreeSpecies.objects.all():
        climates = [value.strip().casefold() for value in tree.recommended_climate.split(',')]
        if not any(climate == value for value in climates):
            continue

        soils = [value.strip().casefold() for value in tree.recommended_soil.split(',')]
        score = 2 if soil in soils else 0
        if care_preference and tree.care_level.strip().casefold() == care_preference.strip().casefold():
            score += 1
        if growth_preference and tree.growth_rate.strip().casefold() == growth_preference.strip().casefold():
            score += 1
        candidates.append((score, tree.title.casefold(), tree.pk, tree))

    if not candidates:
        return None
    return sorted(candidates, key=lambda candidate: (-candidate[0], candidate[1], candidate[2]))[0][3]


class CalculateCapsuleView(views.APIView):
    """Принимает форму с Экрана 2 и возвращает рекомендованные параметры"""
    def post(self, request):
        request_serializer = CalculationRequestSerializer(
            data=request.data,
            context={'request': request},
        )
        request_serializer.is_valid(raise_exception=True)
        data = request_serializer.validated_data

        # Логика подбора (упрощённый экспертный алгоритм)
        weight = data['weight']
        capsule_size = "S" if weight < 5 else ("M" if weight <= 20 else "L")
        breakdown = degradation_breakdown(weight, data['soil'], data['climate'])
        
        tree = _matching_tree_species(
            data['climate'],
            data['soil'],
            data['care_level_pref'],
            data['desired_growth_time'],
        )
        pet = None
        if data.get('pet_id') is not None:
            pet = Pet.objects.get(pk=data['pet_id'])

        calculation = CapsuleCalculation.objects.create(
            user=request.user if request.user.is_authenticated else None,
            pet=pet,
            memorial_scenario=data['scenario'],
            region=data['region'],
            climate=data['climate'],
            soil_type=data['soil'],
            lighting=data['lighting'],
            water_proximity=data['water_proximity'],
            care_level_pref=data['care_level_pref'],
            desired_growth_time=data['desired_growth_time'],
            weight_kg=weight,
            recommended_capsule_material="Мицелий с прессованным торфом",
            recommended_capsule_size=f"{capsule_size} (до {weight} кг)",
            est_degradation_time=f"{breakdown['total_months']:.1f} месяца",
            estimated_degradation_months=breakdown['total_months'],
            recommended_tree=tree,
            comment=data['comment'],
        )
        
        serializer = CalculationSerializer(calculation)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class PetListCreateView(generics.ListCreateAPIView):
    serializer_class = PetSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Pet.objects.filter(user=self.request.user).order_by('id')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class PetDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PetSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Pet.objects.filter(user=self.request.user)


class TreeSpeciesListView(generics.ListAPIView):
    queryset = TreeSpecies.objects.all().order_by('title', 'id')
    serializer_class = TreeSpeciesSerializer

class DownloadPDFPassportView(views.APIView):
    """Generate a PDF passport from the saved calculation and pet details."""
    def get(self, request, calculation_id):
        calculation = get_object_or_404(
            CapsuleCalculation.objects.select_related('pet', 'recommended_tree'),
            pk=calculation_id,
        )
        buffer = io.BytesIO()
        font_path = Path(__file__).resolve().parents[1] / 'assets' / 'fonts' / 'NotoSans.ttf'
        if 'NotoSans' not in pdfmetrics.getRegisteredFontNames():
            pdfmetrics.registerFont(TTFont('NotoSans', str(font_path)))
            pdfmetrics.registerFont(TTFont('NotoSans-Bold', str(font_path)))
            pdfmetrics.registerFontFamily(
                'NotoSans',
                normal='NotoSans',
                bold='NotoSans-Bold',
                italic='NotoSans',
                boldItalic='NotoSans-Bold',
            )

        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(
            name='PassportTitle',
            parent=styles['Title'],
            fontName='NotoSans-Bold',
            fontSize=11,
            leading=16,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#718078'),
            spaceAfter=4 * mm,
        ))
        styles.add(ParagraphStyle(
            name='PassportHeading',
            parent=styles['Heading2'],
            fontName='NotoSans-Bold',
            fontSize=11,
            leading=15,
            textColor=colors.HexColor('#1f513d'),
            backColor=colors.HexColor('#eaf3ec'),
            borderPadding=(6, 8, 6, 8),
            spaceBefore=5 * mm,
            spaceAfter=3 * mm,
        ))
        styles.add(ParagraphStyle(
            name='PassportBody',
            parent=styles['BodyText'],
            fontName='NotoSans',
            fontSize=9,
            leading=13,
            wordWrap='CJK',
        ))
        styles.add(ParagraphStyle(
            name='PassportLabel',
            parent=styles['BodyText'],
            fontName='NotoSans-Bold',
            fontSize=9,
            leading=13,
            textColor=colors.HexColor('#244438'),
        ))

        def paragraph(value, style='PassportBody'):
            return Paragraph(escape(str(value or '—')), styles[style])

        def section(title, rows):
            story.append(Paragraph(escape(title), styles['PassportHeading']))
            table = Table(
                [[paragraph(label, 'PassportLabel'), paragraph(value)] for label, value in rows],
                colWidths=[52 * mm, 118 * mm],
                hAlign='LEFT',
            )
            table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#fbfcfa')),
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f5f0')),
                ('LINEBELOW', (0, 0), (-1, -2), 0.35, colors.HexColor('#dce7df')),
                ('LEFTPADDING', (0, 0), (-1, -1), 9),
                ('RIGHTPADDING', (0, 0), (-1, -1), 9),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ]))
            story.extend([table, Spacer(1, 2 * mm)])

        story = [
            Paragraph('ВАША ИСТОРИЯ ПРОДОЛЖАЕТ РАСТИ', styles['PassportTitle']),
            Table(
                [[
                    Paragraph(f'<b>ПАСПОРТ №{calculation.pk}</b>', styles['PassportBody']),
                    Paragraph(f'Создан {calculation.created_at:%d.%m.%Y}', styles['PassportBody']),
                ]],
                colWidths=[85 * mm, 85 * mm],
                style=TableStyle([
                    ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f4f1de')),
                    ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#244438')),
                    ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 11),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 11),
                    ('TOPPADDING', (0, 0), (-1, -1), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 9),
                    ('ROUNDEDCORNERS', [4, 4, 4, 4]),
                ]),
            ),
            Spacer(1, 3 * mm),
        ]
        pet = calculation.pet
        if pet:
            if pet.photo:
                try:
                    photo_path = pet.photo.path
                    if os.path.isfile(photo_path):
                        photo = Image(photo_path, width=45 * mm, height=45 * mm, kind='proportional')
                        photo.hAlign = 'LEFT'
                        story.extend([photo, Spacer(1, 3 * mm)])
                    else:
                        logger.warning('Pet photo file is missing for pet id=%s', pet.pk)
                except (OSError, ValueError):
                    logger.exception('Unable to include pet photo in calculation PDF, pet id=%s', pet.pk)
            section('Данные питомца', [
                ('Имя', pet.name),
                ('Вид', pet.species),
                ('Порода', pet.breed),
                ('Вес', f'{pet.weight_kg:g} кг'),
                ('Возраст на дату ухода', f'{pet.age_at_death_years} лет' if pet.age_at_death_years is not None else ''),
                ('Дата рождения', pet.birth_date.strftime('%d.%m.%Y') if pet.birth_date else ''),
                ('Дата ухода', pet.death_date.strftime('%d.%m.%Y') if pet.death_date else ''),
            ])

        section('Параметры, указанные пользователем', [
            ('Вес для расчёта', f'{calculation.weight_kg:g} кг' if calculation.weight_kg is not None else (f'{pet.weight_kg:g} кг' if pet else '')),
            ('Сценарий мемориала', calculation.memorial_scenario),
            ('Регион', calculation.region),
            ('Климат', calculation.climate),
            ('Тип почвы', calculation.soil_type),
            ('Освещённость', calculation.lighting),
            ('Близость воды', calculation.water_proximity),
            ('Предпочтительный уход', calculation.care_level_pref),
            ('Желаемый темп роста', calculation.desired_growth_time),
            ('Комментарий', calculation.comment),
        ])
        calculation_weight = calculation.weight_kg if calculation.weight_kg is not None else (pet.weight_kg if pet else None)
        model_description = '—'
        if calculation_weight is not None:
            try:
                factors = degradation_breakdown(calculation_weight, calculation.soil_type, calculation.climate)
            except KeyError:
                logger.warning('Cannot reproduce biodegradation estimate for legacy calculation id=%s', calculation.pk)
                model_description = 'Невозможно воспроизвести: неизвестная категория почвы или климата'
            else:
                model_description = (
                    f"Ttotal = {factors['base_months']:g} × {factors['k_weight']:g} × "
                    f"{factors['k_soil']:g} × {factors['k_climate']:g} = "
                    f"{factors['total_months']:.1f} месяца"
                )
        section('Рекомендация', [
            ('Материал капсулы', calculation.recommended_capsule_material),
            ('Размер капсулы', calculation.recommended_capsule_size),
            ('Срок разложения', calculation.est_degradation_time),
            ('Модель срока', model_description),
            ('Рекомендуемое дерево', calculation.recommended_tree.title if calculation.recommended_tree else 'Не подобрано'),
        ])

        document = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=20 * mm,
            leftMargin=20 * mm,
            topMargin=18 * mm,
            bottomMargin=18 * mm,
            title=f'Паспорт живого мемориала №{calculation.pk}',
        )
        def draw_page(canvas, doc):
            canvas.saveState()
            page_width, page_height = A4
            canvas.setFillColor(colors.HexColor('#1f513d'))
            canvas.rect(0, page_height - 30 * mm, page_width, 30 * mm, fill=1, stroke=0)
            canvas.setFillColor(colors.white)
            canvas.setFont('NotoSans-Bold', 17)
            canvas.drawString(20 * mm, page_height - 17 * mm, 'EcoPet Planner')
            canvas.setFont('NotoSans', 8)
            canvas.setFillColor(colors.HexColor('#dcece1'))
            canvas.drawString(20 * mm, page_height - 23 * mm, 'ПАМЯТЬ, КОТОРАЯ РАСТЁТ')
            canvas.setFillColor(colors.HexColor('#d6955c'))
            canvas.circle(page_width - 24 * mm, page_height - 15 * mm, 8 * mm, fill=1, stroke=0)
            canvas.setStrokeColor(colors.HexColor('#dce7df'))
            canvas.line(20 * mm, 14 * mm, page_width - 20 * mm, 14 * mm)
            canvas.setFillColor(colors.HexColor('#718078'))
            canvas.setFont('NotoSans', 7)
            canvas.drawString(20 * mm, 9 * mm, 'Паспорт живого мемориала')
            canvas.drawRightString(page_width - 20 * mm, 9 * mm, f'{doc.page}')
            canvas.restoreState()

        document.build(story, onFirstPage=draw_page, onLaterPages=draw_page)
        buffer.seek(0)
        response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="memorial-{calculation.pk}.pdf"'
        return response