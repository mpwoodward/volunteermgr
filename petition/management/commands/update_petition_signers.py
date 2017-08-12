from datetime import date, datetime
import re

from dateutil.parser import parse as dateparse
from openpyxl import load_workbook

from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand
from django.core.validators import validate_email

from gis.models import ZipCode
from petition.models import PetitionSigner
from volunteer.models import Volunteer

ZIP_REGEX = re.compile('^\d{5}(\-\d{4})?$')


class Command(BaseCommand):
    help = 'Imports petition signer data from data dump from SpeakOut! plugin for WordPress'

    def add_arguments(self, parser):
        parser.add_argument('--file', help='Path to XLSX file')
        parser.add_argument('--date_signed', help='The starting date for the date signed (optional)')

    def handle(self, *args, **options):
        if not options.get('file', False):
            print('--file is required')
            exit(1)

        wb = load_workbook(options['file'])
        ws = wb.get_active_sheet()
        rowcount = 0
        savedcount = 0

        date_signed = None
        if options.get('date_signed', False):
            try:
                date_signed = dateparse(options.get('date_signed'))
            except ValueError:
                print('Invalid date for date_signed!')
                exit(1)

        for row in ws.rows:
            dt_signed = None
            if row[12].value:
                if isinstance(row[12].value, date) or isinstance(row[12].value, datetime):
                    dt_signed = row[12].value
                elif isinstance(row[12].value, str):
                    try:
                        dt_signed = dateparse(row[12].value.strip())
                    except ValueError:
                        print('INVALID VALUE FOR DATE/TIME SIGNED! Skipping ...')
                        continue

            if date_signed:
                if dt_signed.date() < date_signed.date():
                    print('dt_signed older than date_signed. Skipping ...')
                    continue

            email = None
            if row[4].value and isinstance(row[4].value, str):
                try:
                    email = row[4].value.strip().lower()
                    validate_email(email)
                except ValidationError:
                    print('INVALID EMAIL! {} Skipping ...'.format(row[4].value))
                    continue

            first_name = None
            if row[2].value and isinstance(row[2].value, str):
                first_name = row[2].value.strip().title()

            last_name = None
            if row[3].value and isinstance(row[3].value, str):
                last_name = row[3].value.strip().title()

            zip = None
            non_conforming_zip = None
            if row[8].value:
                zip = str(row[8].value).strip()

                # if it's only 4 characters and all numbers, throw in a leading 0
                if len(zip) == 4:
                    try:
                        int(zip)
                        zip = '0{}'.format(zip)
                    except ValueError:
                        pass

                # if it's 9 characters and all numbers, throw in a -
                if len(zip) == 9:
                    try:
                        int(zip)
                        zip = '{}-{}'.format(zip[:5], zip[5:])
                    except ValueError:
                        pass

                # if we get to here and still don't have a valid zip, we'll throw it in the non-conforming field
                if not re.match(ZIP_REGEX, zip):
                    non_conforming_zip = zip
                    zip = None

            city = None
            state = None
            if zip:
                try:
                    zipcode = ZipCode.objects.get(zip=zip[:5])
                    city = zipcode.city
                    state = zipcode.state
                except ZipCode.DoesNotExist:
                    print('COULD NOT DETERMINE STATE FROM ZIP {}!'.format(zip))

            try:
                PetitionSigner.objects.get(email__iexact=email)
                print('PETITION SIGNER FOR EMAIL {} EXISTS! Skipping ...'.format(email))
                continue
            except PetitionSigner.DoesNotExist:
                print('NO PETITION SIGNER FOR EMAIL {}! Creating ...'.format(email))
                PetitionSigner.objects.create(
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    city=city,
                    state=state,
                    zip=zip,
                    non_conforming_zip=non_conforming_zip,
                    dt_signed=dt_signed
                )

                savedcount += 1

            # if the petition signer is also a volunteer, update the signed date
            try:
                volunteer = Volunteer.objects.get(email__iexact=email)
                print('Volunteer found for email {}! Updating petition signed date ...'.format(email))
                volunteer.dt_signed_petition = dt_signed
                volunteer.save()
            except Volunteer.DoesNotExist:
                pass

            rowcount += 1

        print('*** PROCESSING COMPLETE. {} rows processed, {} petition signers created.'.format(rowcount, savedcount))
