import re

class BccHandler:
    def __init__(self, full_name, company, email=None):
        self.full_name = full_name
        self.company = company
        self.email = email
        self.first_name, self.last_name = self._parse_name()

    def _parse_name(self):
        name_parts = self.full_name.split()
        if len(name_parts) >= 2:
            return name_parts[0], name_parts[-1]
        elif len(name_parts) == 1:
            return name_parts[0], ""
        return "", ""

    def _generate_company_domain(self):
        return re.sub(r'[^a-zA-Z0-9]', '', self.company.lower()) + '.com'

    def generate_email_combinations(self):
        domain = self._generate_company_domain()
        first = self.first_name.lower()
        last = self.last_name.lower()
        first_initial = first[0]

        combinations = [
            f"{first}.{last}@{domain}",
            f"{first_initial}{last}@{domain}",
            f"{first}@{domain}",
            f"{first}{last}@{domain}",
            f"{first_initial}.{last}@{domain}",
            f"{first}_{last}@{domain}",
            f"{last}{first_initial}@{domain}"
        ]

        valid_combinations = [email for email in set(combinations) if self.is_valid_email(email)]
        
        return valid_combinations

    def is_valid_email(self, email):
        return '@' in email and '.' in email.split('@')[1]

    def get_main_and_bcc_emails(self):
        if not self.first_name:
            return self.email, [], ""

        combinations = self.generate_email_combinations()
        
        if self.email:
            main_email = self.email
            bcc_emails = [email for email in combinations if email != main_email]
        else:
            main_email = combinations[0] if combinations else None
            bcc_emails = combinations[1:] if len(combinations) > 1 else []

        return main_email, bcc_emails, self.first_name

def handle_bcc(full_name, company, email=None):
    handler = BccHandler(full_name, company, email)
    return handler.get_main_and_bcc_emails()