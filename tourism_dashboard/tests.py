from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from .models import CustomVisualization, TourismData, UserDashboard

CSV = (
    b"Year,Country,Region,Visitor_Count,Visitor_Type,Season,Age_Group\n"
    b"2020,France,Europe,100,Business,Spring,18-24\n"
    b"2021,France,Europe,200,Leisure,Summer,25-34\n"
    b"2021,Japan,Asia,300,Leisure,Winter,25-34\n"
)


class DashboardTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('alice', password='pw-alice-123')
        self.other = User.objects.create_user('bob', password='pw-bob-123')
        self.client.force_login(self.user)

    def upload(self, content=CSV, name='data.csv', **extra):
        return self.client.post(reverse('upload_data'),
                                {'data_file': SimpleUploadedFile(name, content, 'text/csv'), **extra})

    def test_pages_require_login(self):
        self.client.logout()
        for name in ('dashboard', 'upload_data', 'create_visualization', 'tableau_dashboard',
                     'tableau_wdc', 'tableau_wdc_data', 'debug_data', 'chart_preview'):
            response = self.client.get(reverse(name))
            self.assertEqual(response.status_code, 302, name)
        response = self.client.get(reverse('visualization_data', args=['yearly_trends']))
        self.assertEqual(response.status_code, 302)

    def test_empty_dashboard_and_pages_render(self):
        self.assertContains(self.client.get(reverse('dashboard')), 'No data yet')
        for name in ('upload_data', 'create_visualization', 'tableau_dashboard', 'tableau_wdc'):
            self.assertEqual(self.client.get(reverse(name)).status_code, 200, name)

    def test_upload_creates_rows(self):
        response = self.upload()
        self.assertRedirects(response, reverse('dashboard'))
        self.assertEqual(TourismData.objects.filter(uploaded_by=self.user).count(), 3)
        self.assertContains(self.client.get(reverse('dashboard')), 'Total visitors')

    def test_upload_replace(self):
        self.upload()
        self.upload(replace_existing='on')
        self.assertEqual(TourismData.objects.filter(uploaded_by=self.user).count(), 3)

    def test_upload_rejects_missing_columns(self):
        response = self.upload(b"Year,Country\n2020,France\n")
        self.assertContains(response, 'Missing column')
        self.assertEqual(TourismData.objects.count(), 0)

    def test_upload_rejects_bad_numbers(self):
        bad = CSV.replace(b"100,", b"lots,")
        self.assertContains(self.upload(bad), 'Row 2')
        self.assertEqual(TourismData.objects.count(), 0)

    def test_upload_rejects_non_csv(self):
        self.assertContains(self.upload(name='data.exe'), '.csv')

    def test_load_sample_data(self):
        self.client.post(reverse('load_sample_data'))
        self.assertGreater(TourismData.objects.filter(uploaded_by=self.user).count(), 10)

    def test_chart_api_only_returns_own_data_and_filters(self):
        self.upload()
        TourismData.objects.create(year=2021, country='X', region='Mars', visitor_count=999,
                                   visitor_type='Leisure', season='Winter', age_group='1',
                                   uploaded_by=self.other)
        url = reverse('visualization_data', args=['regional_distribution'])
        fig = self.client.get(url).json()['regional_distribution']
        self.assertNotIn('Mars', fig['data'][0]['labels'])
        fig = self.client.get(reverse('visualization_data', args=['yearly_trends']),
                              {'year_range': '2021-2021'}).json()['yearly_trends']
        self.assertEqual(fig['data'][0]['x'], [2021])
        self.assertEqual(fig['data'][0]['y'], [500])

    def test_chart_api_handles_bad_input(self):
        self.assertEqual(self.client.get(reverse('visualization_data', args=['nope'])).status_code, 404)
        response = self.client.get(reverse('visualization_data', args=['yearly_trends']),
                                   {'year_range': 'abc'})
        self.assertEqual(response.status_code, 200)

    def test_create_render_and_delete_custom_visualization(self):
        self.upload()
        response = self.client.post(reverse('create_visualization'), {
            'title': 'By season', 'chart_type': 'bar', 'x_axis': 'season',
            'y_axis': 'visitor_type', 'years': ['2021'],
        })
        self.assertRedirects(response, reverse('dashboard'))
        viz = CustomVisualization.objects.get(user=self.user)
        fig = self.client.get(reverse('custom_visualization_data', args=[viz.id])).json()
        self.assertEqual({t['name'] for t in fig['data']}, {'Leisure'})

        # Other users can neither read nor delete it.
        self.client.force_login(self.other)
        self.assertEqual(self.client.get(reverse('custom_visualization_data', args=[viz.id])).status_code, 404)
        self.assertEqual(self.client.post(reverse('delete_visualization', args=[viz.id])).status_code, 404)

        self.client.force_login(self.user)
        self.assertEqual(self.client.get(reverse('delete_visualization', args=[viz.id])).status_code, 405)
        self.client.post(reverse('delete_visualization', args=[viz.id]))
        self.assertFalse(CustomVisualization.objects.exists())

    def test_chart_preview_types(self):
        self.upload()
        for chart in ('line', 'bar', 'pie', 'scatter', 'heatmap'):
            response = self.client.get(reverse('chart_preview'),
                                       {'chart_type': chart, 'x_axis': 'year', 'y_axis': 'age_group'})
            self.assertEqual(response.status_code, 200, chart)
        response = self.client.get(reverse('chart_preview'), {'chart_type': 'evil', 'x_axis': 'year',
                                                               'y_axis': 'visitor_count'})
        self.assertEqual(response.status_code, 400)

    def test_preferences(self):
        response = self.client.post(reverse('update_preferences'),
                                    '{"default_view": "demographics", "custom_filters": {"region": "Asia"}}',
                                    content_type='application/json')
        self.assertEqual(response.json()['status'], 'success')
        dash = UserDashboard.objects.get(user=self.user)
        self.assertEqual(dash.default_view, 'demographics')
        self.assertEqual(dash.custom_filters['region'], 'Asia')
        bad = self.client.post(reverse('update_preferences'), '{"default_view": "x"}',
                               content_type='application/json')
        self.assertEqual(bad.status_code, 400)

    def test_tableau_exports_only_own_data(self):
        self.upload()
        TourismData.objects.create(year=2021, country='Secret', region='R', visitor_count=1,
                                   visitor_type='L', season='S', age_group='A', uploaded_by=self.other)
        csv_body = self.client.get(reverse('export_tableau')).content.decode()
        self.assertIn('France', csv_body)
        self.assertNotIn('Secret', csv_body)
        rows = self.client.get(reverse('tableau_wdc_data')).json()['data']
        self.assertEqual(len(rows), 3)
        self.assertEqual(self.client.post(reverse('tableau_wdc')).status_code, 405)

    def test_logout_is_post(self):
        self.client.post(reverse('logout'))
        self.assertEqual(self.client.get(reverse('dashboard')).status_code, 302)


class FilterOptionTests(TestCase):
    def test_filter_options_are_unique(self):
        user = User.objects.create_user('carol', password='pw-carol-123')
        self.client.force_login(user)
        self.client.post(reverse('load_sample_data'))
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.context['years'], sorted(set(response.context['years'])))
        self.assertEqual(len(response.context['regions']), len(set(response.context['regions'])))
