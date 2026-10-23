from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import EcoZone


class EcoZoneApiTests(APITestCase):
	def setUp(self):
		user_model = get_user_model()
		self.user = user_model.objects.create_user(
			username='user',
			email='user@example.com',
			password='test-password',
		)
		self.admin = user_model.objects.create_user(
			username='admin',
			email='admin@example.com',
			password='test-password',
			is_staff=True,
		)
		self.initial_zone_count = EcoZone.objects.count()

	def create_zone(self, **overrides):
		values = {
			'name': 'North Park',
			'zone_type': 'Memorial forest',
			'address': 'North district',
			'latitude': 60.0,
			'longitude': 30.0,
			'rules': 'Follow park rules',
		}
		values.update(overrides)
		return EcoZone.objects.create(**values)

	def test_public_list_returns_active_zones_only(self):
		active_zone = self.create_zone()
		closed_zone = self.create_zone(name='Closed Park', is_active=False)

		response = self.client.get(reverse('zone_list'))

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		response_ids = [zone['id'] for zone in response.data]
		self.assertIn(active_zone.id, response_ids)
		self.assertNotIn(closed_zone.id, response_ids)

	def test_non_admin_cannot_manage_zones(self):
		self.client.force_authenticate(self.user)

		response = self.client.post(reverse('admin_zone_list_create'), {
			'name': 'New Park',
			'zone_type': 'Forest',
			'address': 'North district',
			'latitude': 60.0,
			'longitude': 30.0,
			'rules': 'Follow park rules',
		})

		self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
		self.assertEqual(EcoZone.objects.count(), self.initial_zone_count)

	def test_admin_can_create_update_and_delete_zone(self):
		self.client.force_authenticate(self.admin)
		create_response = self.client.post(reverse('admin_zone_list_create'), {
			'name': 'New Park',
			'zone_type': 'Forest',
			'address': 'North district',
			'latitude': 60.0,
			'longitude': 30.0,
			'rules': 'Follow park rules',
			'is_active': True,
		})
		self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
		zone_url = reverse('admin_zone_detail', args=[create_response.data['id']])

		update_response = self.client.patch(zone_url, {'name': 'Updated Park'})
		self.assertEqual(update_response.status_code, status.HTTP_200_OK)
		self.assertEqual(update_response.data['name'], 'Updated Park')

		delete_response = self.client.delete(zone_url)
		self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)
		self.assertEqual(EcoZone.objects.count(), self.initial_zone_count)
