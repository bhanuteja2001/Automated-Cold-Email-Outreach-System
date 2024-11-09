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
        return name_parts[0], ""

    def _generate_company_domain(self):
        return re.sub(r'[^a-zA-Z0-9]', '', self.company.lower()) + '.com'

    def generate_email_combinations(self):
        if self.email:
            return self.email.split('@')[1]
        return re.sub(r'[^a-zA-Z0-9]', '', self.company.lower()) + '.com'

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
        return list(set(combinations))  # Remove duplicates

    def get_main_and_bcc_emails(self):
        if not self.first_name or not self.last_name:
            return self.email, [], self.first_name

        combinations = self.generate_email_combinations()
        
        if self.email:
            main_email = self.email
            bcc_emails = combinations
        else:
            main_email = combinations[0] if combinations else None
            bcc_emails = combinations[1:] if combinations else []

        return main_email, bcc_emails, self.first_name

def handle_bcc(full_name, company, email=None):
    handler = BccHandler(full_name, company, email)
    return handler.get_main_and_bcc_emails()