# domain_big_data
Retrieve registration data from domainbigdata.com

This repository contains two scripts designed to retreive registration data from the websited domainbigdata.om

The file 'DomainBigData_fromDomain.py' receives a domain and returns the details of the domain registrar including his/her name, address and contact information.  This script is designed to find individuals who registered a domain and not representitives of hosting companies, thus the script filters out individuals with over 100 domains under their name.

The file 'DomainBigData_toDomain.py' receives a name or contact information and returns any domains registered by the input data.

Both of these scripts were written as Maltego transforms thus they both receive their inputs from a Maltego map and return entities created based and the results.
