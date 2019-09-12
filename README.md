Dockerfile for Grafana
===============================================
For dashboard part of Prometheus Monitoring Solution, made some
modification and customize the Grafana Dockerfile.


Grafana Version
---------------
4.4.0

Main Change
-----------
1. Add sys-tools, logrotate and change the timezone.
2. Add Grafana LDAP configuration files.
3. Customize the endpoint script.
4. Add Grafana API script for datasource, dashboard and notify channel
   operations.
