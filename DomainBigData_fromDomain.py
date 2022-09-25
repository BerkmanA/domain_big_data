#!/usr/bin/env python
# @aberkman

from maltego_trx.transform import DiscoverableTransform
from maltego_trx.entities import Person, Organization, Email, Location, PhoneNumber
from maltego_trx.maltego import UIM_PARTIAL, UIM_FATAL
from pycountry_convert import country_name_to_country_alpha2
import requests
import re
import bs4


class DomainBigData_fromDomain(DiscoverableTransform):
    """
    receive domain and check domainbigdata.com for registration details
    creates entities based on results
    """

    @classmethod
    def create_entities(cls, request, response):
        # check domain is working
        if requests.get('https://domainbigdata.com').status_code == 503:
            response.addUIMessage('domainbigdata.com is down', UIM_FATAL)
            return

        # get registration dict
        domain = request.Value
        registrant = cls.get_registration(domain)
        if not registrant:
            return

        # create entities
        labels = ['Person', 'Organization', 'Email', 'Location', 'Name_note', 'Organization_note', 'Email_note']
        entities = [Person, Organization, Email]

        try:
            # create person, organization and email entities
            indx = 0
            while indx < 3:
                if registrant[labels[indx]]:
                    ent = response.addEntity(entities[indx], registrant[labels[indx]])
                    if registrant[labels[indx+4]]:
                        ent.setNote(registrant[labels[indx+4]])
                indx += 1

            # create location entity
            if registrant['Location']:
                flag = False

                # set address
                adr = registrant['Location']['Address']
                if adr:
                    flag = True
                    ent = response.addEntity(Location, adr)
                    ent.addProperty('streetaddress', 'Street Address', '', adr)

                # set city
                city = registrant['Location']['City']
                if city:
                    if not flag:
                        flag = True
                        ent = response.addEntity(Location, city)
                        ent.addProperty('city', 'City', '', city)

                # set state
                state = registrant['Location']['State']
                if state:
                    if not flag:
                        flag = True
                        ent = response.addEntity(Location, state)
                        ent.addProperty('location.area', 'Area', '', state)

                # set country
                cntr = registrant['Location']['Country']
                if cntr:
                    if not flag:
                        flag = True
                        ent = response.addEntity(Location, cntr)
                        ent.addProperty('country', 'Country', '', cntr)
                        ent.addProperty('countrycode', 'Country Code', '', country_name_to_country_alpha2(cntr))

            # create phone entity
            phone = registrant['Phone']
            if phone:
                response.addEntity(PhoneNumber, phone)
        except IOError:
            response.addUIMessage("An error occurred retrieving properties", messageType=UIM_PARTIAL)

    @staticmethod
    def get_registration(domain):
        registrant = {'Person': 0, 'Organization': 0, 'Email': 0, 'Location': 0,
                      'Name_note': 0, 'Organization_note': 0, 'Email_note': 0, 'Phone': 0}

        # get html from domainbigdatat.com
        url = f'https://domainbigdata.com/{domain}'
        sc = requests.get(url).text
        soup = bs4.BeautifulSoup(sc, "lxml")

        # get registration details
        tags = ['#trRegistrantName', '#MainMaster_trRegistrantOrganization', '#trRegistrantEmail']
        labels = ['Person', 'Organization', 'Email', 'Location', 'Name_note', 'Organization_note', 'Email_note']

        indx = 0
        while indx < len(tags):
            item = soup.select(tags[indx])
            if item:
                item = item[0].select('td')
                insert = item[1].get_text()
                insert_note = item[2].get_text()
                insert_note = re.sub(r'[\r\n\t]*', '', insert_note).strip()
                if insert_note == 'is associated with 100+ domains':
                    break
                registrant[labels[indx]] = insert
                registrant[labels[indx + 4]] = insert_note
            indx += 1

        # get registrants address
        address = {'Address': 0, 'City': 0, 'State': 0, 'Country': 0}
        tags = ['#trRegistrantAddress', '#trRegistrantCity', '#trRegistrantState', '#trRegistrantCountry']
        labels = ['Address', 'City', 'State', 'Country']

        indx = 0
        flag = False
        while indx < len(tags):
            item = soup.select(tags[indx])
            if item:
                flag = True
                item = item[0].select('td')
                insert = item[1].get_text().strip()
                address[labels[indx]] = insert
            indx += 1

        if flag:
            registrant['Location'] = address

        # get phone
        item = soup.select('#trRegistrantTel')
        if item:
            item = item[0].select('td')
            insert = item[1].get_text()
            registrant['Phone'] = insert

        return registrant
