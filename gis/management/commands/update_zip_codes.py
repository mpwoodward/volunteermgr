import re

from openpyxl import load_workbook

from django.core.management.base import BaseCommand

from gis.models import ZipCode

ZIP_REGEX = re.compile('^\d{5}(\-\d{4})?$')


class Command(BaseCommand):
    help = 'Imports zip code geodata from a spreadsheet'

    def add_arguments(self, parser):
        parser.add_argument('--file', help='Path to XLSX file')
        parser.add_argument('--worksheet', help='The worksheet name in the spreadsheet file')

    def handle(self, *args, **options):
        if not options.get('file', False) or not options.get('worksheet', False):
            print('--file and --worksheet are required')
            exit(1)

        wb = load_workbook(options['file'])
        ws = wb.get_sheet_by_name(options['worksheet'])
        rowcount = 0
        savedcount = 0

        for row in ws.rows:
            if row[0].value == 'Zip Code':
                continue

            zip = None
            if row[0].value:
                if isinstance(row[0].value, str):
                    zip = row[0].value.strip()
                elif isinstance(row[0].value, int):
                    zip = str(row[0].value)

                if len(zip) < 5:
                    zip = zip.zfill(5)

            if not zip:
                print('COULD NOT DETERMINE ZIP CODE! Skipping ...')
                continue

            city = row[1].value.strip()
            state = row[3].value.strip()

            county = None
            if row[4].value and isinstance(row[4].value, str):
                county = row[4].value.strip()

            lat = None
            if row[5].value and isinstance(row[5].value, float):
                lat = row[5].value

            long = None
            if row[6].value and isinstance(row[6].value, float):
                long = row[6].value

            print(zip, city, state, county, lat, long)

            zipcode = None
            try:
                zipcode = ZipCode.objects.get(zip=zip)
                print('ZIP CODE {} EXISTS! Skipping ...'.format(zip))
                continue
            except ZipCode.DoesNotExist:
                print('NO ZIP CODE {}! Creating ...'.format(zip))
                zipcode = ZipCode.objects.create(
                    zip=zip,
                    state=state,
                    city=city,
                    county=county,
                    lat=lat,
                    long=long
                )

                savedcount += 1

            rowcount += 1

        print('*** PROCESSING COMPLETE. {} rows processed, {} zip codes created.'.format(rowcount, savedcount))
