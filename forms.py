import datetime
import phonenumbers

from wtforms import MultipleFileField, StringField, SelectMultipleField, IntegerField, PasswordField, SubmitField, DateField, \
    HiddenField, validators, SelectField, BooleanField, \
    TextAreaField
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
import email_validator
from wtforms.validators import DataRequired, Optional, ValidationError, URL

import api_calls

from flask_login import current_user


class UploadForm(FlaskForm):
    ALLOWED_EXTENSIONS = {'pdf', 'docx'}

    files = FileField('Upload PDF Files', validators=[
        FileRequired(),

        FileAllowed(ALLOWED_EXTENSIONS, 'Only PDF files are allowed.'),
        FileAllowed(ALLOWED_EXTENSIONS, 'Only pdf and docx files are allowed.')
    ])


class LoginForm(FlaskForm):
    email = StringField('Email')
    password = PasswordField('Password')
    submit = SubmitField('Log In')


class RegisterForm(FlaskForm):
    firstname = StringField('First Name')
    lastname = StringField('Last Name')
    phone_number = StringField('Mobile')
    username = StringField('Username')
    email = StringField('Email', validators=[validators.Email(), validators.DataRequired()])
    password = PasswordField('Password', validators=[
        validators.DataRequired(),
        validators.Length(min=6),
        validators.Regexp(
            regex="^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]",
            message="Password must contain at least one lowercase letter, one uppercase letter, one digit, and one special character."
        )
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        validators.EqualTo('password', message='Passwords must match.')
    ])
    submit = SubmitField('Register')

class JobseekerRegisterForm(FlaskForm):
    firstname = StringField('First Name')
    lastname = StringField('Last Name')
    country_code = SelectField('Country Code', choices=[], validators=[validators.DataRequired()])
    phone_number = StringField('Mobile', validators=[validators.DataRequired()])
    email = StringField('Email', validators=[validators.Email(), validators.DataRequired()])
    password = PasswordField('Password', validators=[
        validators.DataRequired(),
        validators.Length(min=6),
        validators.Regexp(
            regex="^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]",
            message="Password must contain at least one lowercase letter, one uppercase letter, one digit, and one special character."
        )
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        validators.EqualTo('password', message='Passwords must match.')
    ])
    submit = SubmitField('Register')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Populate the country_code dropdown dynamically
        country_list = []
        from phonenumbers.phonenumberutil import COUNTRY_CODE_TO_REGION_CODE
        for code, regions in COUNTRY_CODE_TO_REGION_CODE.items():
            if str(code) == "001":  # Exclude non-geographic codes
                continue
            for region in regions:
                country_list.append((region,region))
        # Sort and assign choices to the SelectField
        self.country_code.choices = sorted(country_list, key=lambda x: x[1])

    # Custom validator for phone_number
    def validate_phone_number(self, field):
        try:
            country_code = self.country_code.data
            if not country_code:
                raise ValidationError("Country code is required.")

            # Parse and validate the phone number
            parsed_number = phonenumbers.parse(field.data, country_code)
            if not phonenumbers.is_valid_number(parsed_number):
                raise ValidationError("Invalid phone number for the selected country.")
        except phonenumbers.NumberParseException:
            raise ValidationError("Invalid phone number format.")


class AdminRegisterForm(FlaskForm):
    username = StringField('Username', validators=[validators.Length(min=4, max=25), validators.DataRequired()])
    email = StringField('Email', validators=[validators.Email(), validators.DataRequired()])
    password = PasswordField('Password', validators=[
        validators.DataRequired(),
        validators.Length(min=6),
        validators.Regexp(
            regex="^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]",
            message="Password must contain at least one lowercase letter, one uppercase letter, one digit, and one special character."
        )
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        validators.EqualTo('password', message='Passwords must match.')
    ])
    submit = SubmitField('Register')


class CompanyRegisterForm(FlaskForm):
    company_logo = FileField('Upload a File', validators=[
        FileRequired(message="Logo file is required")
    ])
    name = StringField('Name', validators=[DataRequired()])
    company_subdomain = StringField('Subdomain', validators=[DataRequired()])
    website_url = StringField('Website URL', validators=[DataRequired()])
    location = StringField('Location',  validators=[DataRequired(message='This field is required.')])
    description = TextAreaField('Descripton')
    submit = SubmitField('Register')

    def validate_company_name(self, field):
        if not field.data:
            raise ValidationError("Company name cannot be empty")

    def validate_website_url(self, field):
        if not field.data:
            raise ValidationError("Website URL cannot be empty")


class AdminAddUserForm(FlaskForm):
    username = StringField('Username', validators=[validators.Length(min=4, max=25), validators.DataRequired()])
    email = StringField('Email', validators=[validators.Email(), validators.DataRequired()])
    password = PasswordField('Password', validators=[
        validators.DataRequired(),
        validators.Length(min=6),
        validators.Regexp(
            regex="^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]",
            message="Password must contain at least one lowercase letter, one uppercase letter, one digit, and one special character."
        )
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        validators.EqualTo('password', message='Passwords must match.')
    ])
    role = SelectField('Select Role :', choices=['user', 'admin'])
    security_group = SelectField('Select Security Group :')
    submit = SubmitField('Add')

    def __init__(self, *args, **kwargs):
        super(AdminAddUserForm, self).__init__(*args, **kwargs)
        self.security_group.choices = self.load_security_groups()

    def load_security_groups(self):
        # Placeholder for loading data from an API
        try:
            security_groups = api_calls.get_all_security_groups(access_token=current_user.id)
            # Replace this with actual async logic to fetch data
            sec = [(security_group['id'], security_group['name']) for security_group in security_groups]
            print(sec)
            return [(security_group['id'], security_group['name']) for security_group in security_groups]
        except:
            return []


class UserPasswordUpdateForm(FlaskForm):
    current_password = PasswordField('Password', validators=[
        validators.DataRequired(),
        validators.Length(min=6),
        validators.Regexp(
            regex="^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]",
            message="Password must contain at least one lowercase letter, one uppercase letter, one digit, and one special character."
        )
    ])
    new_password = PasswordField('Password', validators=[
        validators.DataRequired(),
        validators.Length(min=6),
        validators.Regexp(
            regex="^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]",
            message="Password must contain at least one lowercase letter, one uppercase letter, one digit, and one special character."
        )
    ])
    confirm_new_password = PasswordField('Confirm Password', validators=[
        validators.EqualTo('new_password', message='Passwords must match.')
    ])
    submit = SubmitField('Update Password')


class ForgetPasword(FlaskForm):
    email = StringField('Email')
    submit = SubmitField('Submit')


class ResetPasswordForm(FlaskForm):
    new_password = PasswordField('Password', validators=[
        validators.DataRequired(),
        validators.Length(min=6),
        validators.Regexp(
            regex="^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]",
            message="Password must contain at least one lowercase letter, one uppercase letter, one digit, and one special character."
        )
    ])
    confirm_new_password = PasswordField('Confirm Password', validators=[
        validators.EqualTo('new_password', message='Passwords must match.')
    ])
    submit = SubmitField('Submit')


class AdminEditUserForm(FlaskForm):
    username = StringField('Username', validators=[validators.Length(min=4, max=25), validators.DataRequired()])

    role = SelectField('Select Role :', choices=['user', 'admin'])
    status = SelectField('Select Status :', choices=['active', 'block'])
    submit = SubmitField('Save')


class AdminAddServiceForm(FlaskForm):
    name = StringField('name', validators=[validators.DataRequired()])
    description = StringField('description', validators=[validators.DataRequired()])
    submit = SubmitField('Add Service')


class AdminEditServiceForm(FlaskForm):
    name = StringField('Name', validators=[validators.DataRequired()])
    description = StringField('Description', validators=[validators.DataRequired()])
    submit = SubmitField('Update Service')


class AdminEditCompanyForm(FlaskForm):
    name = StringField('Name')
    website_url = StringField('Website')
    submit = SubmitField('Update Company')


class EmployerProfileForm(FlaskForm):
    # Personal Details
    firstname = StringField('First Name', validators=[DataRequired()])
    lastname = StringField('Last Name', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), validators.Email()])
    phone_number = StringField('Phone Number', validators=[DataRequired()])
    profile_picture = FileField('Profile Picture')

    # Company Details
    company_name = StringField('Company Name', validators=[DataRequired()])
    company_location = StringField('Location', validators=[DataRequired()])
    company_website = StringField('Company Website', validators=[DataRequired()])
    company_description = TextAreaField('Company Description', validators=[DataRequired()])
    company_logo = FileField('Company Logo')

    # Submit buttons
    submit = SubmitField('Save Changes')
    cancel = SubmitField('Cancel')

class UserEditUserForm(FlaskForm):
    profile_picture = FileField('Profile Picture', render_kw={"id": "profile_picture_input", "style": "display: none;"})
    username = StringField('Username', validators=[validators.Length(min=4, max=25), validators.DataRequired()],
                           render_kw={"readonly": True})
    email = StringField('Email', validators=[validators.Email(), validators.DataRequired()],
                        render_kw={"readonly": True})
    company_name = StringField('Username', validators=[validators.DataRequired()],
                           render_kw={"readonly": True})
    company_location = StringField('Username', validators=[validators.DataRequired()],
                           render_kw={"readonly": True})
    company_description = TextAreaField('Description',render_kw={"readonly": True})
    company_website = StringField('Website', validators=[validators.DataRequired()],
                                   render_kw={"readonly": True})
    company_logo = FileField('Company Logo', render_kw={"id": "company_logo", "style": "display: none;"})
    submit = SubmitField('Save')


class EmailFunctionalityForm(FlaskForm):
    smtp_server = StringField('SMTP Server')
    smtp_port = IntegerField('SMTP Port')
    smtp_username = StringField('SMTP Username')
    smtp_password = StringField('SMTP Password')
    sender_email = StringField('Sender Email')
    submit = SubmitField('Save')


class ServiceForm(FlaskForm):
    submit = SubmitField('Save')


class AddPlan(FlaskForm):
    name = StringField('Plan Name', validators=[validators.DataRequired()])
    duration = StringField('Duration (Months)', validators=[validators.DataRequired()])
    fees = IntegerField('Fees', validators=[Optional()])
    is_free = BooleanField('Free')
    unlimited_resume_parsing = BooleanField('Unlimited')
    num_resume_parsing = StringField('Number of Resume Parsings', validators=[Optional()])
    plan_details = TextAreaField('Plan Details',
                                 render_kw={'rows': 30, 'cols': 30, 'placeholder': 'Enter plan details here...'})
    submit = SubmitField('Add Plan')


class AddPost(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    category = SelectField('Category', validators=[DataRequired()], choices=[('', 'Select a category')])
    subcategory = SelectField('Subcategory', validators=[DataRequired()], choices=[('', 'Select a subcategory')])
    content = TextAreaField('Content', render_kw={'rows': 30, 'cols': 30, 'id': 'content',
                                                                               'placeholder': 'Write details about the post.'})
    tags = StringField('Tags', render_kw={
        'placeholder': 'Enter tags, separated by commas',
        'id': 'tags'
    })  # New field for tags

    publish = SubmitField('Publish')
    save_draft = SubmitField('Save Draft')


class AddJobOpening(FlaskForm):
    job_title = StringField('Position', validators=[DataRequired(message='This field is required')])
    target_date = DateField('Target Date', default=lambda: (datetime.datetime.now() + datetime.timedelta(days=60)))
    opening_date = DateField('Opening Date', default=datetime.datetime.now())
    job_type = SelectField('Job Type', default='Full Time',choices=[('', 'Select Type'), ('Full Time', 'Full Time'), ('Part Time', 'Part Time'), ('Training', 'Training'), ('Freelance', 'Freelance'), ('Seasonal', 'Seasonal'), ('Contract', 'Contract'), ('Temporary', 'Temporary')])
    work_experience= SelectField('Work Experience', choices=[('', 'Select Experience'),('Fresher', 'Fresher'),('0-1 years', '0-1 years'),('1-3 years', '1-3 years'), ('3-5 years', '3-5 years'), ('5+ years', '5+ years')])
    industry= SelectField('Industry')
    salary= StringField('Salary')
    address_city= StringField('City')
    address_country= StringField('Country')
    address_province= StringField('Province')
    address_postal_code= StringField('Postal Code')
    job_description= TextAreaField('Job Description' , render_kw={'rows': 30, 'cols': 30, 'id': 'job_description'})
    job_requirements= TextAreaField('Job Requirements', render_kw={'rows': 30, 'cols': 30, 'id': 'job_requirements'})
    job_benefits= TextAreaField('Job Benefits', render_kw={'rows': 30, 'cols': 30, 'id': 'job_benefits'})
    job_opening_status = SelectField('Job Opening Status', default='Active', choices=[('', 'Select status'),('Active', 'Active')])
    publish = SubmitField('Publish Job')
    save_draft = SubmitField('Save Draft')
    preview = SubmitField('Preview')

    def __init__(self, *args, **kwargs):
        super(AddJobOpening, self).__init__(*args, **kwargs)
        self.industry.choices = self.load_industry_choices()


    def load_industry_choices(self):
        INDUSTRY_CHOICES = [
        ('', 'Select Industry'),
        ('Accounting', 'Accounting'),
        ('Airlines/Aviation', 'Airlines/Aviation'),
        ('Alternative Dispute Resolution', 'Alternative Dispute Resolution'),
        ('Alternative Medicine', 'Alternative Medicine'),
        ('Animation', 'Animation'),
        ('Apparel & Fashion', 'Apparel & Fashion'),
        ('Architecture & Planning', 'Architecture & Planning'),
        ('Arts & Crafts', 'Arts & Crafts'),
        ('Automotive', 'Automotive'),
        ('Aviation & Aerospace', 'Aviation & Aerospace'),
        ('Banking', 'Banking'),
        ('Biotechnology', 'Biotechnology'),
        ('Broadcast Media', 'Broadcast Media'),
        ('Building Materials', 'Building Materials'),
        ('Business Supplies & Equipment', 'Business Supplies & Equipment'),
        ('Capital Markets', 'Capital Markets'),
        ('Chemicals', 'Chemicals'),
        ('Civic & Social Organization', 'Civic & Social Organization'),
        ('Civil Engineering', 'Civil Engineering'),
        ('Commercial Real Estate', 'Commercial Real Estate'),
        ('Computer & Network Security', 'Computer & Network Security'),
        ('Computer Games', 'Computer Games'),
        ('Computer Hardware', 'Computer Hardware'),
        ('Computer Networking', 'Computer Networking'),
        ('Computer Software', 'Computer Software'),
        ('Construction', 'Construction'),
        ('Consumer Electronics', 'Consumer Electronics'),
        ('Consumer Goods', 'Consumer Goods'),
        ('Consumer Services', 'Consumer Services'),
        ('Cosmetics', 'Cosmetics'),
        ('Dairy', 'Dairy'),
        ('Defense & Space', 'Defense & Space'),
        ('Design', 'Design'),
        ('Education Management', 'Education Management'),
        ('E-learning', 'E-learning'),
        ('Electrical & Electronic Manufacturing', 'Electrical & Electronic Manufacturing'),
        ('Entertainment', 'Entertainment'),
        ('Environmental Services', 'Environmental Services'),
        ('Events Services', 'Events Services'),
        ('Executive Office', 'Executive Office'),
        ('Facilities Services', 'Facilities Services'),
        ('Farming', 'Farming'),
        ('Financial Services', 'Financial Services'),
        ('Fine Art', 'Fine Art'),
        ('Fishery', 'Fishery'),
        ('Food & Beverages', 'Food & Beverages'),
        ('Food Production', 'Food Production'),
        ('Fundraising', 'Fundraising'),
        ('Furniture', 'Furniture'),
        ('Gambling & Casinos', 'Gambling & Casinos'),
        ('Glass, Ceramics & Concrete', 'Glass, Ceramics & Concrete'),
        ('Government Administration', 'Government Administration'),
        ('Government Relations', 'Government Relations'),
        ('Graphic Design', 'Graphic Design'),
        ('Health, Wellness & Fitness', 'Health, Wellness & Fitness'),
        ('Higher Education', 'Higher Education'),
        ('Hospital & Health Care', 'Hospital & Health Care'),
        ('Hospitality', 'Hospitality'),
        ('Human Resources', 'Human Resources'),
        ('Import & Export', 'Import & Export'),
        ('Individual & Family Services', 'Individual & Family Services'),
        ('Industrial Automation', 'Industrial Automation'),
        ('Information Services', 'Information Services'),
        ('Information Technology & Services', 'Information Technology & Services'),
        ('Insurance', 'Insurance'),
        ('International Affairs', 'International Affairs'),
        ('International Trade & Development', 'International Trade & Development'),
        ('Internet', 'Internet'),
        ('Investment Banking/Venture', 'Investment Banking/Venture'),
        ('Investment Management', 'Investment Management'),
        ('Judiciary', 'Judiciary'),
        ('Law Enforcement', 'Law Enforcement'),
        ('Law Practice', 'Law Practice'),
        ('Legal Services', 'Legal Services'),
        ('Legislative Office', 'Legislative Office'),
        ('Leisure & Travel', 'Leisure & Travel'),
        ('Libraries', 'Libraries'),
        ('Logistics & Supply Chain', 'Logistics & Supply Chain'),
        ('Luxury Goods & Jewelry', 'Luxury Goods & Jewelry'),
        ('Machinery', 'Machinery'),
        ('Management Consulting', 'Management Consulting'),
        ('Maritime', 'Maritime'),
        ('Marketing & Advertising', 'Marketing & Advertising'),
        ('Market Research', 'Market Research'),
        ('Mechanical or Industrial Engineering', 'Mechanical or Industrial Engineering'),
        ('Media Production', 'Media Production'),
        ('Medical Device', 'Medical Device'),
        ('Medical Practice', 'Medical Practice'),
        ('Mental Health Care', 'Mental Health Care'),
        ('Military', 'Military'),
        ('Mining & Metals', 'Mining & Metals'),
        ('Motion Pictures & Film', 'Motion Pictures & Film'),
        ('Museums & Institutions', 'Museums & Institutions'),
        ('Music', 'Music'),
        ('Nanotechnology', 'Nanotechnology'),
        ('Newspapers', 'Newspapers'),
        ('Nonprofit Organization Management', 'Nonprofit Organization Management'),
        ('Oil & Energy', 'Oil & Energy'),
        ('Online Publishing', 'Online Publishing'),
        ('Outsourcing/Offshoring', 'Outsourcing/Offshoring'),
        ('Package/Freight Delivery', 'Package/Freight Delivery'),
        ('Packaging & Containers', 'Packaging & Containers'),
        ('Paper & Forest Products', 'Paper & Forest Products'),
        ('Performing Arts', 'Performing Arts'),
        ('Pharmaceuticals', 'Pharmaceuticals'),
        ('Philanthropy', 'Philanthropy'),
        ('Photography', 'Photography'),
        ('Plastics', 'Plastics'),
        ('Political Organization', 'Political Organization'),
        ('Primary/Secondary', 'Primary/Secondary'),
        ('Printing', 'Printing'),
        ('Professional Training', 'Professional Training'),
        ('Program Development', 'Program Development'),
        ('Public Policy', 'Public Policy'),
        ('Public Relations', 'Public Relations'),
        ('Public Safety', 'Public Safety'),
        ('Publishing', 'Publishing'),
        ('Railroad Manufacture', 'Railroad Manufacture'),
        ('Ranching', 'Ranching'),
        ('Real Estate', 'Real Estate'),
        ('Recreational', 'Recreational'),
        ('Facilities & Services', 'Facilities & Services'),
        ('Religious Institutions', 'Religious Institutions'),
        ('Renewables & Environment', 'Renewables & Environment'),
        ('Research', 'Research'),
        ('Restaurants', 'Restaurants'),
        ('Retail', 'Retail'),
        ('Security & Investigations', 'Security & Investigations'),
        ('Semiconductors', 'Semiconductors'),
        ('Shipbuilding', 'Shipbuilding'),
        ('Sporting Goods', 'Sporting Goods'),
        ('Sports', 'Sports'),
        ('Staffing & Recruiting', 'Staffing & Recruiting'),
        ('Supermarkets', 'Supermarkets'),
        ('Telecommunications', 'Telecommunications'),
        ('Textiles', 'Textiles'),
        ('Think Tanks', 'Think Tanks'),
        ('Tobacco', 'Tobacco'),
        ('Translation & Localization', 'Translation & Localization'),
        ('Transportation/Trucking/Railroad', 'Transportation/Trucking/Railroad'),
        ('Utilities', 'Utilities'),
        ('Venture Capital', 'Venture Capital'),
        ('Veterinary', 'Veterinary'),
        ('Warehousing', 'Warehousing'),
        ('Wholesale', 'Wholesale'),
        ('Wine & Spirits', 'Wine & Spirits'),
        ('Wireless', 'Wireless'),
        ('Writing & Editing', 'Writing & Editing')
    ]
        return INDUSTRY_CHOICES





class AddPage(FlaskForm):
    title = StringField('title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()],
                            render_kw={'rows': 30, 'cols': 30, 'id': 'content',
                                       'placeholder': 'Write details about the post.'})
    publish = SubmitField('Publish')
    save_draft = SubmitField('Save Draft')


class AddCategory(FlaskForm):
    category = StringField('Category title', validators=[validators.DataRequired()])
    submit = SubmitField('Add Category')


class AddSubcategory(FlaskForm):
    subcategory = StringField('Subcategory title', validators=[validators.DataRequired()])
    category = SelectField('Category', coerce=int, validators=[DataRequired()], default='Select Category')
    submit = SubmitField('Add Subcategory')


class AddTag(FlaskForm):
    tag = StringField('Tag title', validators=[validators.DataRequired()])
    submit = SubmitField('Add Tag')


class EditTag(FlaskForm):
    tag = StringField('Tag title', validators=[validators.DataRequired()])
    submit = SubmitField('Update Tag')


class AdminUpdatePost(FlaskForm):
    title = StringField('Post title', validators=[validators.DataRequired()])
    category = SelectField('Category', validators=[DataRequired()], choices=[('', 'Select a category')])
    subcategory = SelectField('Subcategory', validators=[DataRequired()], choices=[('', 'Select a subcategory')])
    tags = SelectField('Tags', validators=[DataRequired()], choices=[('', 'Select a tag')])
    content = TextAreaField('Content', render_kw={'rows': 30, 'cols': 30, 'placeholder': 'Enter Content here...'})
    submit = SubmitField('Update Post')


class CreateEmailTemplate(FlaskForm):
    name = StringField('Name', validators=[validators.DataRequired()])
    subject = StringField('Subject', validators=[validators.DataRequired()])
    content = TextAreaField('Write Email here ...',
                            render_kw={'rows': 10, 'cols': 30, 'placeholder': 'Enter Content here...'})
    submit = SubmitField('Create Template')


class UpdateEmailTemplate(FlaskForm):
    name = StringField('Name', validators=[validators.DataRequired()])
    subject = StringField('Subject', validators=[validators.DataRequired()])
    content = TextAreaField('Write Email here ...',
                            render_kw={'rows': 10, 'cols': 30, 'placeholder': 'Enter Content here...'})
    submit = SubmitField('Update Template')


class SendEmail(FlaskForm):
    to = StringField('To', validators=[validators.DataRequired()])
    subject = StringField('Subject', validators=[validators.DataRequired()])
    content = TextAreaField('Content', render_kw={'rows': 10, 'cols': 30, 'placeholder': 'Enter Content here...'})
    submit = SubmitField('Send Mail')


class AddMediaForm(FlaskForm):
    files = MultipleFileField('Media Files', validators=[DataRequired()])
    submit = SubmitField('Upload')


class CreateNewsletterForm(FlaskForm):
    name = StringField('Name', validators=[validators.DataRequired()],
                       render_kw={'placeholder': 'Give a name to your Newsletter'})
    description = TextAreaField('Description', validators=[validators.DataRequired()],
                                render_kw={'rows': 3, 'placeholder': 'Describe what your newsletter is about'})
    submit = SubmitField('Submit')


class SubscribeToNewsletterForm(FlaskForm):
    name = StringField('Name', validators=[validators.DataRequired()],
                       render_kw={'placeholder': 'Name'})
    email = StringField('Email', validators=[validators.DataRequired()],
                        render_kw={'placeholder': 'Email'})
    submit = SubmitField('Subscribe to my Newsletter')


class UnsubscribeToNewsletterForm(FlaskForm):
    email = StringField('Email', validators=[validators.DataRequired()],
                        render_kw={'placeholder': 'Email'})
    submit = SubmitField('Unsubscribe')


class ApplyToJob(FlaskForm):
    job_id = HiddenField()
    resume = SelectField('Resume')
    upload_resume = FileField('Upload Resume')
    apply = SubmitField('Apply')

    def __init__(self, *args, **kwargs):
        super(ApplyToJob, self).__init__(*args, **kwargs)
        self.resume.choices = self.load_my_resumes()

    def load_my_resumes(self):
        # Placeholder for loading data from an API
        try:
            resumes = api_calls.get_user_all_medias(access_token=current_user.id)
            print(len(resumes))
            # Replace this with actual async logic to fetch data
            return [('', 'Select Resume from My Resumes')] + [(res['id'], res['filename']) for res in resumes]
        except:
            return []

class AddTrackers(FlaskForm):
    name = StringField('Name', validators=[validators.DataRequired()])
    description = TextAreaField('Description')
    on_apply = BooleanField('On Apply')
    job_status = StringField('Status')
    submit = SubmitField('Create Tracker')

################################################# JOBSEEKER FORMS ########################################################

class AboutForm(FlaskForm):
    about = TextAreaField('About', validators=[validators.DataRequired()])
    submit = SubmitField('Add About Me')

class EducationForm(FlaskForm):
    institution_name = StringField('Institution Name', validators=[DataRequired()])
    degree = StringField('Degree', validators=[DataRequired()])
    field_of_study = StringField('Field of Study', validators=[Optional()])
    start_date = DateField('Start Date', format='%Y-%m-%d', validators=[Optional()])
    end_date = DateField('End Date', format='%Y-%m-%d', validators=[Optional()])
    ongoing = BooleanField('Ongoing')
    submit = SubmitField('Add Education')


class ExperienceForm(FlaskForm):
    company_name = StringField('Company Name', validators=[DataRequired()])
    position = StringField('Position', validators=[DataRequired()])
    start_date = DateField('Start Date', format='%Y-%m-%d', validators=[Optional()])
    end_date = DateField('End Date', format='%Y-%m-%d', validators=[Optional()])
    ongoing = BooleanField('Ongoing')
    responsibilities = TextAreaField('Responsibilities', validators=[DataRequired()])
    submit = SubmitField('Add Experience')


class InternshipForm(FlaskForm):
    company_name = StringField('Company Name', validators=[DataRequired()])
    position = StringField('Position', validators=[DataRequired()])
    start_date = DateField('Start Date', format='%Y-%m-%d', validators=[Optional()])
    end_date = DateField('End Date', format='%Y-%m-%d', validators=[Optional()])
    ongoing = BooleanField('Ongoing')
    job_description = TextAreaField('Job Description', validators=[Optional()])
    submit = SubmitField('Add Internship')

class ProjectForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[Optional()])
    project_url = StringField('Project URL', validators=[Optional()])
    submit = SubmitField('Add Project')

class AccomplishmentForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[Optional()])
    achievement_date = DateField('Achievement Date', format='%Y-%m-%d', validators=[Optional()])
    submit = SubmitField('Add Accomplishment')


class CollectNameForm(FlaskForm):

    firstname = StringField('First Name', validators=[DataRequired()])
    lastname = StringField('Last Name', validators=[DataRequired()])
    submit = SubmitField('Change Name')


class CollectEmailForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    submit = SubmitField('Change Email')


class CollectPhoneForm(FlaskForm):
    phone_number = StringField('Mobile', validators=[DataRequired()])
    submit = SubmitField('Change Mobile')

class CollectProfilePictureForm(FlaskForm):
    ALLOWED_EXTENSIONS = ['jpg', 'jpeg', 'png']
    profile_picture = FileField('Profile Picture', validators=[FileRequired(),FileAllowed(ALLOWED_EXTENSIONS, 'Only JPEG, PNG, and JPG files are allowed!')])
    submit = SubmitField('Upload Picture')

