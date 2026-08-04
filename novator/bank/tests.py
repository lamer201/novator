from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from bank.models import Balance
from main.models import Team, UserProfile

User = get_user_model()


class ZakazBalanceContextTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.team = Team.objects.create(name='Команда 1', slug='team-1', status=True)
        self.user_profile = UserProfile.objects.create(user=self.user, role='manager')
        self.user_profile.teams.add(self.team)
        self.balance = Balance.objects.create(team=self.team, money=12345.67)

    def test_truba_order_page_includes_balance_context(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('bank:create_zakaz_many_item'), {'category': 'truba'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['balance'].team, self.team)
