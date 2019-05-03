import babel.numbers
import csv
import sys


q2017 = ['2016-2017-Q4', '2017-2018-Q1', '2017-2018-Q2', '2017-2018-Q3']

organizations = {}

with open(sys.argv[1], 'r') as contracts_file:
    c_reader = csv.DictReader(contracts_file, dialect='excel')
    row_num = 0
    for c_record in c_reader:
        try:
            if c_record['reporting_period'] in q2017:
                org_id = c_record['owner_org']
                current_org = {}
                if org_id in organizations:
                    current_org = organizations[org_id]
                else:
                    org_titles = c_record['owner_org_title'].split('|')
                    #org_title_en = org_titles[0]
                    #org_title_fr = org_titles[1] if len(org_titles) > 1 else org_titles[0]
                    current_org = {'year': 2017,
                                   'service_original': 0,
                                   'service_amendment': 0,
                                   'service_count': 0,
                                   'goods_original': 0,
                                   'goods_amendment': 0,
                                   'goods_count': 0,
                                   'construction_original': 0,
                                   'construction_amendment': 0,
                                   'construction_count': 0,
                                   }
                ov = babel.numbers.parse_decimal(c_record['original_value'].replace('$', ''), locale='en_CA')
                av = babel.numbers.parse_decimal(c_record['amendment_value'].replace('$', ''), locale='en_CA')
                if c_record['commodity_type_code'] == 'S':
                    current_org['service_original'] += ov
                    current_org['service_amendment'] += av
                    current_org['service_count'] += 1
                elif c_record['commodity_type_code'] == 'G':
                    current_org['goods_original'] += ov
                    current_org['goods_amendment'] += av
                    current_org['goods_count'] += 1
                elif c_record['commodity_type_code'] == 'C':
                    current_org['construction_original'] += ov
                    current_org['construction_amendment'] += av
                    current_org['construction_count'] += 1
                organizations[org_id] = current_org
                row_num += 1

        except Exception as x:
            sys.stderr.write(repr(x))

for org in organizations:
    print(repr(org))

    print(row_num)
