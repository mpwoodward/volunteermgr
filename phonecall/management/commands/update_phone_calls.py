from dateutil.parser import parse as dateparse
from localflavor.us.us_states import US_STATES
from openpyxl import load_workbook

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand
from django.core.validators import validate_email

from gis.models import ZipCode
from organization.models import Organization
from phonecall.models import PhoneCall
from security.models import User
from volunteer.models import Volunteer


class Command(BaseCommand):
    help = 'Imports phone calls from Maestro Conferencing export'

    def add_arguments(self, parser):
        parser.add_argument('--file', help='Path to XLSX file')
        parser.add_argument('--call_date', help='The date of the conference call')

    def handle(self, *args, **options):
        if not options.get('file', False) or not options.get('call_date', False):
            print('--file and --call_date are required')
            exit(1)

        volunteer_contenttype = ContentType.objects.get_for_model(Volunteer)
        staff_contenttype = ContentType.objects.get_for_model(User)

        call_date = options['call_date']
        try:
            call_date = dateparse(call_date)
        except ValueError:
            print('INVALID CALL DATE!')
            exit(0)

        wb = load_workbook(options['file'])
        ws = wb.get_active_sheet()
        headercount = 0
        rowcount = 0
        savedcount = 0

        for row in ws.rows:
            if headercount < 1:  # skip header row
                headercount += 1
                continue
            else:
                pin = str(row[0].value).strip()
                caller_id = str(row[1].value).strip()

                first_name = None
                last_name = None
                if row[3].value and isinstance(row[3].value, str):
                    name = row[3].value.strip()

                    if len(name.split(' ')) == 1:
                        first_name = name
                    else:
                        first_name = ' '.join(name.split(' ')[:-1]).title()
                        last_name = ' '.join(name.split(' ')[-1:]).title()

                email = None
                if row[4].value and isinstance(row[4].value, str):
                    try:
                        email = row[4].value.strip().lower()
                        validate_email(email)
                    except ValidationError:
                        print('INVALID EMAIL{}! Skipping ...'.format(row[4].value))
                        continue
                else:
                    print('BLANK EMAIL! Skipping ...')
                    continue

                zip = None
                if row[5].value:
                    zip = str(row[5].value).strip()
                    if len(zip) == 4:
                        zip = '0{}'.format(zip)

                state = None
                if row[6].value and isinstance(row[6].value, str):
                    s = row[6].value.strip()

                    if len(s) == 2:
                        state = s.upper()
                    elif s.find('(') != -1:  # sometimes comes through e.g. Florida (FL)
                        state = s[s.find('(') + 1:-1].upper()
                    else:
                        for item in US_STATES:
                            if item[1] == s:
                                state = item[0]
                                break

                if zip and not state:  # try to get the state from the zip
                    try:
                        zipcode = ZipCode.objects.get(zip=zip[:5])
                        state = zipcode.state
                    except ZipCode.DoesNotExist:
                        pass

                city = None
                if zip:  # try to get the city from the zip
                    try:
                        zipcode = ZipCode.objects.get(zip=zip[:5])
                        city = zipcode.city
                    except ZipCode.DoesNotExist:
                        pass

                organization = None
                if state:
                    organization = Organization.objects.filter(state=state).first()

                if not organization:
                    print('ORGANIZATION NOT FOUND! {}'.format(state))
                    continue

                start = row[7].value
                end = row[8].value
                duration = row[9].value

                notes = None
                if row[11].value and isinstance(row[11].value, str):
                    notes = row[11].value.strip()

                # caller could be either staff or volunteer; check staff first
                staff = None
                ct = None
                object_id = None
                content_object = None
                try:
                    staff = User.objects.get(email__iexact=email)
                    ct = staff_contenttype
                    object_id = staff.id
                    content_object = staff
                    print('USER {} FOUND. Saving phone call ...'.format(email))
                except User.DoesNotExist:
                    print("Email {} doesn't match any staff. Checking volunteers ...".format(email))

                volunteer = None
                if not staff:
                    try:
                        volunteer = Volunteer.objects.get(email__iexact=email)
                        ct = volunteer_contenttype
                        object_id = volunteer.id
                        content_object = volunteer
                        print('VOLUNTEER {} FOUND. Saving phone call ...'.format(email))
                    except Volunteer.DoesNotExist:
                        print("Email {} doesn't match any volunteers. Saving as caller ...".format(email))

                try:
                    PhoneCall.objects.create(
                        content_type=ct,
                        object_id=object_id,
                        content_object=content_object,
                        call_date=call_date,
                        pin=pin,
                        first_name=first_name,
                        last_name=last_name,
                        caller_id=caller_id,
                        email=email,
                        city=city,
                        state=state,
                        zip=zip,
                        start=start,
                        end=end,
                        duration=duration,
                        notes=notes,
                    )
                    savedcount += 1
                except Exception as e:
                    print('SAVING CALL FAILED! {}'.format(str(e)))
                    continue

                rowcount += 1

        print('*** PROCESSING COMPLETE. {} rows processed, {} calls created or updated.'.format(rowcount, savedcount))
