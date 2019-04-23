import csv

import xlrd


def main(xlsx_path):
    wb = xlrd.open_workbook(xlsx_path)
    registered_emails = set()
    voters = []
    for sheet in wb.sheets():
        for i, row in enumerate(sheet.get_rows()):
            # Skip headers
            if i == 0:
                continue
            firstname, lastname, _, _, _, _, email = [
                cell.value for cell in row
            ]
            if not email or email in registered_emails:
                continue
            registered_emails.add(email)
            voters.append((firstname.strip(), lastname.strip(), email))

    with open("TNUPA-voters.csv", "w") as f:
        csv_writer = csv.writer(f)
        csv_writer.writerows(voters)


if __name__ == "__main__":
    voters = "TNUPA-voters.xlsx"
    sheet = main(voters)
