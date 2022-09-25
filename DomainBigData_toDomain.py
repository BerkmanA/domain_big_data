#!/usr/bin/env python
# @aberkman

from maltego_trx.transform import DiscoverableTransform
from maltego_trx.entities import Website
from maltego_trx.maltego import UIM_PARTIAL, UIM_FATAL
import requests
import bs4


class DomainBigData_toDomain(DiscoverableTransform):
    """
    receive ip, name, email and check domainbigdata.com for domains
    returns domains registered under input
    """

    @classmethod
    def create_entities(cls, request, response):
        # check domain is working
        if requests.get('https://domainbigdata.com').status_code == 503:
            response.addUIMessage('domainbigdata.com is down', UIM_FATAL)
            return

        query = request.Value
        html = ''
        domains = []

        # identify query type and call relevant function
        if '@' in query: # is email
            html = cls.get_html('email', query)
            domains = cls.check_name_email(html)
        elif '.' in query: # is ip
            html = cls.get_html('ip', query)
            domains = cls.check_ip(html)
        else: # is name
            html = cls.get_html('name', query)
            domains = cls.check_name_email(html)

        try:
            # add entities
            for domain in domains:
                response.addEntity(Website, domain)
        except IOError:
            response.addUIMessage("An error occurred retrieving properties", messageType=UIM_PARTIAL)

    @staticmethod
    def get_html(tag, query):
        host = "domainbigdata.com"
        query = f'/{tag}/%s' % query
        url = "http://%s%s" % (host, query)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.122 Safari/537.36'}
        req = requests.get(url, headers=headers)
        html = bs4.BeautifulSoup(req.text, "lxml")
        return html

    @staticmethod
    def check_ip(sc):
        domains = []
        item = sc.select('#divDomainSameIP')
        if item:
            item = item[0].select('div')
            item = item[0].get_text()
            domains = item.split('\n')
            domains = domains[5:-3]
        return domains

    @staticmethod
    def check_name_email(sc):
        domains = []
        indx = 0
        item = sc.select(f'#MainMaster_rptWebsitesForName_trrptWebsitesForName_{indx}')
        while item:
            item = item[0].select('td')
            domain = item[0].get_text()
            domains.append(domain)
            indx += 1
            item = sc.select(f'#MainMaster_rptWebsitesForName_trrptWebsitesForName_{indx}')
        return domains
