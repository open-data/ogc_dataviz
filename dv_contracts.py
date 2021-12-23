import argparse
import babel.numbers
import csv
import os
import sys
import traceback

q2017 = ['2016-2017-Q4', '2017-2018-Q1', '2017-2018-Q2', '2017-2018-Q3']
q2018 = ['2017-2018-Q4', '2018-2019-Q1', '2018-2019-Q2', '2018-2019-Q3']
q2019 = ['2018-2019-Q4', '2019-2020-Q1', '2019-2020-Q2', '2019-2020-Q3']

organizations_over_25k = {}
organizations_under_25k = {}

organizations_over_10k = {}
organizations_under_10k = {}

# Usage: python dv_contracts.py <path to quarterly contracts .CSV file> <path to annual contracts .CSV file>

parser = argparse.ArgumentParser()
parser.add_argument("quarterly_contracts", help="The file path of the quarterly contracts .CSV file", )
parser.add_argument("annual_contracts", help="The file path of the consolidated annual contracts .CSV file")
parser.add_argument("output_directory", help="The directory where the .CSV output files should be written.")
parser.parse_args()
args = parser.parse_args()

# Process the quarterly contracts over $10,000 file.

with open(args.quarterly_contracts, 'r', encoding='utf-8-sig') as contracts_file:
    c_reader = csv.DictReader(contracts_file, dialect='excel')
    row_num = 0
    for c_record in c_reader:
        try:
            solicit_code = str(c_record['solicitation_procedure']).strip()
            year = c_record['contract_date'].split("-")[0]
            if solicit_code in ['Non-competitiv SO/SA'] : solicit_code = 'TN'
            if (year in ['2017', '2018', '2019','2020','2021']) and (solicit_code not in ['', 'ZC']):
                org_id = c_record['owner_org']
                # if any(ele in c_record['reference_number'] for ele in q2017):
                #     year = '2017'
                # elif any(ele in c_record['reference_number'] for ele in q2018):
                #     year = '2018'
                # elif any(ele in c_record['reference_number'] for ele in q2019):
                #     year = '2019'

                current_org = {}

                # retrieve contract values and convert to decimal values

                ov = babel.numbers.parse_decimal(c_record['original_value'].replace('$', ''), locale='en_CA') \
                    if not c_record['original_value'] == '' else 0
                cv = babel.numbers.parse_decimal(c_record['contract_value'].replace('$', ''), locale='en_CA') \
                    if not c_record['contract_value'] == '' else 0
                av = babel.numbers.parse_decimal(c_record['amendment_value'].replace('$', ''), locale='en_CA') \
                    if not c_record['amendment_value'] == '' else 0

                # retrieve the existing organization record or create it if it does not exist

                if org_id in organizations_over_10k and year in organizations_over_10k[org_id] and solicit_code in organizations_over_10k[org_id][year]:
                    current_org = organizations_over_10k[org_id][year][solicit_code]
                else:
                    current_org = {'department': c_record['owner_org_title'],
                                   'year': year,
                                   'contact_count': 0,
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

                is_original = (av == 0)
                if is_original:
                    current_org['contact_count'] += 1
                    if c_record['commodity_type'] == 'S':
                        current_org['service_original'] += cv
                        current_org['service_count'] += 1
                    elif c_record['commodity_type'] == 'G':
                        current_org['goods_original'] += cv
                        current_org['goods_count'] += 1
                    elif c_record['commodity_type'] == 'C':
                        current_org['construction_original'] += cv
                        current_org['construction_count'] += 1
                else:
                    current_org['contact_count'] += 1
                    if c_record['commodity_type'] == 'S':
                        current_org['service_amendment'] += av
                    elif c_record['commodity_type'] == 'G':
                        current_org['goods_amendment'] += av
                    elif c_record['commodity_type'] == 'C':
                        current_org['construction_amendment'] += av

                if org_id not in organizations_over_10k:
                    organizations_over_10k[org_id] = {}
                if year not in organizations_over_10k[org_id]:
                    organizations_over_10k[org_id][year] = {}
                organizations_over_10k[org_id][year][solicit_code] = current_org
                row_num += 1

        except Exception as x:
            sys.stderr.write("Error: {0}\n".format(x))
            print(traceback.format_exc())

    print('Processed {0} quarterly contracts rows'.format(row_num))

# Process the annual consolidated contracts under $10,000 file.

with open(args.annual_contracts, 'r', encoding='utf-8-sig') as contractsa_file:
    c_reader = csv.DictReader(contractsa_file, dialect='excel')
    row_num = 0
    for c_record in c_reader:
        year = c_record['year']
        try:
            if year in ['2017','2018','2019','2020','2021']:
                org_id = c_record['owner_org']
                if org_id in organizations_under_10k and year in organizations_under_10k[org_id]:
                    current_org = organizations_under_10k[org_id][year]
                else:
                    current_org = {'department': c_record['owner_org_title'],
                                   'year': c_record['year'],
                                   'contact_count': 0,
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
                gvo = babel.numbers.parse_decimal(c_record['contracts_goods_original_value'], locale='en_CA')
                gva = babel.numbers.parse_decimal(c_record['contracts_goods_amendment_value'], locale='en_CA')
                gno = babel.numbers.parse_number(c_record['contract_goods_number_of'], locale='en_CA')
                svo = babel.numbers.parse_decimal(c_record['contracts_service_original_value'], locale='en_CA')
                sva = babel.numbers.parse_decimal(c_record['contracts_service_amendment_value'], locale='en_CA')
                sno = babel.numbers.parse_number(c_record['contract_service_number_of'], locale='en_CA')
                cvo = babel.numbers.parse_decimal(c_record['contracts_construction_original_value'], locale='en_CA')
                cva = babel.numbers.parse_decimal(c_record['contracts_construction_amendment_value'], locale='en_CA')
                cno = babel.numbers.parse_number(c_record['contract_construction_number_of'], locale='en_CA')

                current_org['contact_count'] += (gno + sno + cno)
                current_org['service_original'] += svo
                current_org['service_amendment'] += sva
                current_org['service_count'] += sno
                current_org['goods_original'] += gvo
                current_org['goods_amendment'] += gva
                current_org['goods_count'] += gno
                current_org['construction_original'] += cvo
                current_org['construction_amendment'] += cva
                current_org['construction_count'] += cno

                if org_id not in organizations_under_10k:
                    organizations_under_10k[org_id] = {}
                organizations_under_10k[org_id][year] = current_org
                row_num += 1

        except Exception as x:
            print(traceback.format_exc())
            sys.stderr.write(repr(x))
    print('Processed {0} annual consolidated contracts rows'.format(row_num))


# Create the under $10K Contracts file for data visualization

with open(os.path.join(args.output_directory, 'contracts_viz_under_10k.csv'), 'w', encoding='utf-8',  newline='') as \
        outfile:
    field_names = ['year', 'commodity_type_en', 'commodity_type_fr', 'contracts_count', 'original_value',
                   'amendment_value', 'department_en', 'department_fr']
    csv_writer = csv.DictWriter(outfile, fieldnames=field_names, dialect='excel')
    csv_writer.writeheader()

    for org in organizations_under_10k:
        for year in organizations_under_10k[org]:
            bi_org_title = str(organizations_under_10k[org][year]['department']).split('|')
            department_en = bi_org_title[0].strip()
            department_fr = bi_org_title[1].strip() if len(bi_org_title) == 2 else department_en
            row_values = {'year': organizations_under_10k[org][year]['year'],
                          'commodity_type_en': 'Service',
                          'commodity_type_fr': 'Services',
                          'contracts_count': organizations_under_10k[org][year]['service_count'],
                          'original_value': organizations_under_10k[org][year]['service_original'],
                          'amendment_value': organizations_under_10k[org][year]['service_amendment'],
                          'department_en': department_en,
                          'department_fr': department_fr}
            csv_writer.writerow(row_values)
            row_values = {'year': organizations_under_10k[org][year]['year'],
                          'commodity_type_en': 'Good',
                          'commodity_type_fr': 'Biens',
                          'contracts_count': organizations_under_10k[org][year]['goods_count'],
                          'original_value': organizations_under_10k[org][year]['goods_original'],
                          'amendment_value': organizations_under_10k[org][year]['goods_amendment'],
                          'department_en': department_en,
                          'department_fr': department_fr}
            csv_writer.writerow(row_values)
            row_values = {'year': organizations_under_10k[org][year]['year'],
                          'commodity_type_en': 'Construction',
                          'commodity_type_fr': 'Construction',
                          'contracts_count': organizations_under_10k[org][year]['construction_count'],
                          'original_value': organizations_under_10k[org][year]['construction_original'],
                          'amendment_value': organizations_under_10k[org][year]['construction_amendment'],
                          'department_en': department_en,
                          'department_fr': department_fr}
            csv_writer.writerow(row_values)


# Create the over $10K Contracts file for data visualization

with open(os.path.join(args.output_directory, 'contracts_viz_over_10k.csv'), 'w', encoding='utf-8',  newline='') as \
        outfile:
    field_names = ['year', 'commodity_type_en', 'commodity_type_fr', 'solicitation_code',
                   'contracts_count', 'original_value',
                   'amendment_value', 'department_en', 'department_fr']
    csv_writer = csv.DictWriter(outfile, fieldnames=field_names, dialect='excel')
    csv_writer.writeheader()

    for org in organizations_over_10k:
        for year in organizations_over_10k[org]:
            for s_code in organizations_over_10k[org][year]:
                bi_org_title = str(organizations_over_10k[org][year][s_code]['department']).split('|')
                department_en = bi_org_title[0].strip()
                department_fr = bi_org_title[1].strip() if len(bi_org_title) == 2 else department_en
                row_values = {'year': organizations_over_10k[org][year][s_code]['year'],
                              'commodity_type_en': 'Service',
                              'commodity_type_fr': 'Services',
                              'solicitation_code': s_code,
                              'contracts_count': organizations_over_10k[org][year][s_code]['service_count'],
                              'original_value': organizations_over_10k[org][year][s_code]['service_original'],
                              'amendment_value': organizations_over_10k[org][year][s_code]['service_amendment'],
                              'department_en': department_en,
                              'department_fr': department_fr}
                csv_writer.writerow(row_values)
                row_values = {'year': organizations_over_10k[org][year][s_code]['year'],
                              'commodity_type_en': 'Good',
                              'commodity_type_fr': 'Biens',
                              'solicitation_code': s_code,
                              'contracts_count': organizations_over_10k[org][year][s_code]['goods_count'],
                              'original_value': organizations_over_10k[org][year][s_code]['goods_original'],
                              'amendment_value': organizations_over_10k[org][year][s_code]['goods_amendment'],
                              'department_en': department_en,
                              'department_fr': department_fr}
                csv_writer.writerow(row_values)
                row_values = {'year': organizations_over_10k[org][year][s_code]['year'],
                              'commodity_type_en': 'Construction',
                              'commodity_type_fr': 'Construction',
                              'solicitation_code': s_code,
                              'contracts_count': organizations_over_10k[org][year][s_code]['construction_count'],
                              'original_value': organizations_over_10k[org][year][s_code]['construction_original'],
                              'amendment_value': organizations_over_10k[org][year][s_code]['construction_amendment'],
                              'department_en': department_en,
                              'department_fr': department_fr}
                csv_writer.writerow(row_values)