#-*- coding:utf-8 -*-
"""
Initialization script for Grafana Monitoring Container Service
    1. Create InfluxDB data source;
    2. Create Dingtalk notification channels;
    3. Create dashboard for Apps in cluster;
"""
import os
from time import sleep
import json
import jinja2
import requests

GRAFANA_BASE_URL = 'http://grafana.CLUSTER.yourdomain.com:3000'
GRAFANA_HEADER = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': 'API_KEY',
}

# Get project from local file.
def get_projects(project_list_path):
    """
    :return: project lists loaded from local file.
    """
    project_list = []
    try:
        with open(project_list_path, 'r') as project_list_file:
            project_list = [project.strip(os.linesep) \
                for project in project_list_file.readlines() \
                if project[0] != '#']
            return project_list
    except IOError as error:
        print('{}: {} is not avaiable.'.format(error, project_list_path))
        return project_list

# Render template for alerting.
def get_dashboard_template(template_path='./template/dashboard.template'):
    """
    :return: template string rendered.
    """
    template = None
    try:
        template_abspath = os.path.abspath(template_path)
        if not os.path.isfile(template_abspath):
            raise IOError
        template_dir, template_name = os.path.dirname(template_abspath), \
                          os.path.basename(template_abspath)
        #
        t_loader = jinja2.FileSystemLoader(searchpath=template_dir)
        t_env = jinja2.Environment(loader=t_loader)
        template = t_env.get_template(template_name)
        return template
    #pylint: disable=W0703
    except IOError:
        print('Cannot get dashboard template in {}.'\
         .format(os.path.join(template_dir, template_name)))
        return template
    except Exception as error:
        print('Render template error: {}.'.format(error))
        return template


#pylint: disable=W0703
class Grafana():
    """
        create grafana:
            data source
            dashboard
            alerting channel
        via API
    """
    # Batch add service monitoring & alerting dashboard on grafana
    @staticmethod
    def create_dashboard(cluster, project, data_source, api_key, template_path):
        """
        create grafana dashboard based on rendered json via grafana API.
        :params:
            cluster: e.g.: k8s-platform
            project: e.g.: sc-call
            data_source: e.g.: k8s-platform-influxdb
            api_key: Grafana页面获取
            template_path: 模版存放路径
        """
        create_dashboard_api = '/api/dashboards/db'
        create_dashboard_header = GRAFANA_HEADER
        create_dashboard_header['Authorization'] = api_key
        try:
            create_dashboard_url = '{}{}'.format(
                GRAFANA_BASE_URL.replace('CLUSTER', cluster),
                create_dashboard_api)
            template = get_dashboard_template(template_path)
            dashboard_data = template.render(
                cluster_name=cluster,
                project_name=project,
                datasource=data_source)
            create_dashboard_response = requests.post(
                create_dashboard_url,
                headers=create_dashboard_header,
                data=dashboard_data)
            print('Dashboard create result: {}.'.format(create_dashboard_response.text))
            return {'Status': 'Success'}
            # avoid post too much application data in one time.
        except Exception as error:
            print('Create dashboard failed:{}.'.format(error))

    # Create influxdb datasource on grafana
    @staticmethod
    def create_influxdb_datasource(cluster, api_key):
        """
        create grafana influxdb datasource via grafana API.
        :params:
            cluster: e.g.: k8s-testing
            api_key: Grafana页面获取
        """
        create_datasource_api = '/api/datasources'
        create_datasource_header = GRAFANA_HEADER
        create_datasource_header['Authorization'] = api_key
        try:
            create_datasource_url = '{}{}'.format(
                GRAFANA_BASE_URL.replace('CLUSTER', cluster),
                create_datasource_api)
            datasource_name = '{}-influxdb'.format(cluster)
            print('Data source: {}.'.format(datasource_name))
            datasource_data = {
                'name': datasource_name,
                'type': 'influxDB',
                'url': 'http://monitoring-influxdb:8086',
                'access': 'proxy',
                'basicAuth': False,
            }
            datasource_data = json.dumps(datasource_data)
            print(datasource_data)
            create_datasource_response = requests.post(
                create_datasource_url,
                headers=create_datasource_header,
                data=datasource_data)
            print('Data Source create result: {}.'\
                .format(create_datasource_response.text))
            return {'Status': 'Success'}
        except Exception as error:
            print('Create data source failed: {}.'.format(error))

    # Create Dingtalk notification channel
    @staticmethod
    def create_dingtalk_channel(cluster, api_key, dingtalk_url):
        """
        create grafana notification channel via Dingtalk.
        """
        create_channel_api = '/api/alert-notifications'
        create_channel_header = GRAFANA_HEADER
        create_channel_header['Authorization'] = api_key
        try:
            create_channel_url = '{}{}'.format(
                GRAFANA_BASE_URL.replace('CLUSTER', cluster),
                create_channel_api)
            channel_name = '{}-dingtalk'.format(cluster)
            print('Channel name: {}.'.format(channel_name))
            create_channel_data = {
                'name': channel_name,
                'type': 'dingding',
                'isDefault': True,
                'settings': {
                    'addresses': dingtalk_url,
                }
            }
            create_channel_data = json.dumps(create_channel_data)
            create_channel_response = requests.post(
                create_channel_url,
                headers=create_channel_header,
                data=create_channel_data)
            print('Create Channel Dingtalk result: {}.'.format(create_channel_response.text))
            return {'Status': 'Success'}
        except Exception as error:
            print('Create Channel failed: {}.'.format(error))


if __name__ == '__main__':
    APPS = get_projects('./project')
    print('Apps: {}.'.format(APPS))
    CLUSTER = os.getenv('CLUSTER', 'your_cluster')
    API_KEY = os.getenv('API_KEY', '')
    DATA_SOURCE = os.getenv('DATA_SOURCE', 'your-influxdb')
    TEMPLATE_PATH = os.getenv('TEMPLATE_PATH', './yaml/dashboard.template')
    DINGTALK_URL = os.getenv('DINGTALK_URL', '')
    #
    Grafana.create_influxdb_datasource(CLUSTER, API_KEY)
    #
    if APPS:
        for app in APPS:
            Grafana.create_dashboard(
                CLUSTER,
                app,
                DATA_SOURCE,
                API_KEY,
                TEMPLATE_PATH)
            sleep(1)
    #
    Grafana.create_dingtalk_channel(CLUSTER, API_KEY, DINGTALK_URL)
