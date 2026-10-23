from io import BytesIO
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from .models import Pet, TreeSpecies


class PetAndTreeSpeciesApiTests(APITestCase):
	def setUp(self):
		self.user = get_user_model().objects.create_user(
			username='owner',
			email='owner@example.com',
			password='test-password',
		)
		self.other_user = get_user_model().objects.create_user(
			username='other',
			email='other@example.com',
			password='test-password',
		)
		self.client.force_authenticate(self.user)

	def test_user_can_create_and_list_only_their_pets(self):
		Pet.objects.create(user=self.other_user, name='Other pet', species='Cat', weight_kg=4)

		response = self.client.post(reverse('pet_list_create'), {
			'name': 'Milo',
			'species': 'Cat',
			'breed': 'Mixed',
			'weight_kg': 4.5,
		})

		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		self.assertEqual(Pet.objects.get(pk=response.data['id']).user, self.user)

		response = self.client.get(reverse('pet_list_create'))
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual([pet['name'] for pet in response.data], ['Milo'])

	def test_user_can_upload_pet_photo_and_profile_details(self):
		image_buffer = BytesIO()
		Image.new('RGB', (1, 1), color='white').save(image_buffer, format='PNG')
		photo = SimpleUploadedFile(
			'pet.png',
			image_buffer.getvalue(),
			content_type='image/png',
		)

		response = self.client.post(reverse('pet_list_create'), {
			'name': 'Milo',
			'species': 'Cat',
			'breed': 'Mixed',
			'weight_kg': 4.5,
			'age_years': 8,
			'birth_date': '2018-04-12',
			'death_date': '2026-09-01',
			'photo': photo,
		}, format='multipart')

		self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
		self.assertTrue(response.data['photo'])
		pet = Pet.objects.get(pk=response.data['id'])
		self.assertEqual(pet.breed, 'Mixed')
		self.assertEqual(pet.age_years, 8)
		self.assertTrue(pet.photo.name)

	def test_user_cannot_access_another_users_pet(self):
		pet = Pet.objects.create(user=self.other_user, name='Other pet', species='Cat', weight_kg=4)

		response = self.client.patch(reverse('pet_detail', args=[pet.pk]), {'name': 'Changed'})

		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		pet.refresh_from_db()
		self.assertEqual(pet.name, 'Other pet')

	def test_user_can_clear_optional_pet_profile_fields(self):
		pet = Pet.objects.create(
			user=self.user,
			name='Milo',
			species='Cat',
			weight_kg=4.5,
			age_years=8,
			birth_date='2018-04-12',
			death_date='2026-09-01',
		)

		response = self.client.patch(
			reverse('pet_detail', args=[pet.pk]),
			{'age_years': '', 'birth_date': '', 'death_date': ''},
			format='multipart',
		)

		self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
		pet.refresh_from_db()
		self.assertIsNone(pet.age_years)
		self.assertIsNone(pet.birth_date)
		self.assertIsNone(pet.death_date)

	def test_tree_species_are_public_and_include_recommendation_fields(self):
		tree = TreeSpecies.objects.create(
			title='Pine',
			growth_rate='Medium',
			care_level='Low',
			lifespan='100 years',
			recommended_climate='Temperate',
			recommended_soil='Loam',
		)
		self.client.force_authenticate(user=None)

		response = self.client.get(reverse('tree_species_list'))

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.data[0]['id'], tree.id)
		self.assertEqual(response.data[0]['recommended_climate'], 'Temperate')

	def test_calculation_saves_required_fields_and_owns_linked_pet(self):
		pet = Pet.objects.create(user=self.user, name='Milo', species='Cat', weight_kg=4.5)
		TreeSpecies.objects.create(
			title='Pine',
			growth_rate='Medium',
			care_level='Low',
			lifespan='100 years',
			recommended_climate='Temperate',
			recommended_soil='Loam',
		)

		response = self.client.post(reverse('calculate'), {
			'weight': 4.5,
			'scenario': 'Memorial tree',
			'region': 'Northwest',
			'climate': 'Temperate',
			'soil': 'Loam',
			'lighting': 'Partial shade',
			'pet_id': pet.id,
		})

		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		self.assertEqual(response.data['pet'], pet.id)
		self.assertEqual(response.data['water_proximity'], '')
		self.assertEqual(response.data['care_level_pref'], '')
		self.assertEqual(response.data['desired_growth_time'], '')

	def test_pdf_passport_contains_saved_calculation_and_pet_data(self):
		pet = Pet.objects.create(
			user=self.user,
			name='Milo',
			species='Cat',
			breed='Mixed',
			weight_kg=4.5,
			age_years=8,
		)
		calculation_response = self.client.post(reverse('calculate'), {
			'weight': 4.5,
			'scenario': 'Memorial tree',
			'region': 'Northwest',
			'climate': 'Temperate',
			'soil': 'Loam',
			'lighting': 'Partial shade',
			'water_proximity': 'Near a pond',
			'care_level_pref': 'Low',
			'desired_growth_time': 'Medium',
			'comment': 'A quiet place',
			'pet_id': pet.id,
		})
		self.assertEqual(calculation_response.status_code, status.HTTP_201_CREATED)

		response = self.client.get(reverse('download_pdf', args=[calculation_response.data['id']]))

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response['Content-Type'], 'application/pdf')
		self.assertIn(b'%PDF', response.content)
		self.assertIn(b'/ToUnicode', response.content)
		self.assertIn(b'memorial-', response['Content-Disposition'].encode())
