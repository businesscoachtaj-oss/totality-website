---
title: File formats and columns
summary: Which files the import accepts, the columns each import type needs, how dates and statuses are read, and how to export from PTminder, ABC Trainerize and Mindbody.
---

This page is the reference for the [Import wizard](import.html): what to put in your spreadsheet so everything comes across cleanly.

## File types

- **CSV** (comma separated values), the most common export format
- **XLS** and **XLSX** (Excel workbooks)
- Exports that come out of a button called "Export" but are really a web table or tab separated text. Mindbody does this. The wizard reads these as they are.

The first row must be your column headings. Each row after that is one record. Up to 2,000 rows per run.

## Columns for each import type

**Bold** fields are required. Column names in your file do not have to match exactly: the wizard guesses, and you can fix any match on the Map Columns step.

### Clients

| Field | Notes |
|---|---|
| **Full Name** | One column with the whole name |
| **Email** | Must be a real email address. Used as the login |
| Phone | |
| Date of Birth | See dates below |
| Membership Status | active, inactive, lead or cancelled (see statuses below) |
| Member Since Date | Their start date |
| Emergency Contact Name | |
| Emergency Contact Phone | |
| Assigned Trainer | The trainer's full name or email, exactly as it is in Totality |

### Trainers / Staff

| Field | Notes |
|---|---|
| **Full Name** | |
| **Email** | Used as their login |
| Phone | |
| Role | Optional. Everyone is imported as a trainer. See the note below |
| Hire Date | |
| Certifications | Comma separated, for example First Aid, Cert IV |

:::note Role column
Everyone in a trainer import is added as a trainer, whatever the Role column says. If any rows say admin, manager or owner, the **Import Complete** screen tells you how many. Only the gym owner can make someone an admin, in the app after the import.
:::

### Payment History

| Field | Notes |
|---|---|
| **Client Email** | Matched to the member with that email |
| **Date** | |
| **Amount** | Dollars, for example 29.00 |
| Description | |
| Payment Method | cash, card, bank transfer or other |
| Status | paid, pending, failed or refunded |

### Membership Types

| Field | Notes |
|---|---|
| **Name** | For example Unlimited |
| Price | Dollars. Blank imports as $0 |
| Billing Cycle | Use weekly, fortnightly, monthly, quarterly or yearly |
| Session Count | Optional number |

### Attendance / Sessions

| Field | Notes |
|---|---|
| **Client Email** | |
| **Date** | |
| Session Name | For example Strength Circuit |
| Status | attended, no-show, cancelled or late-cancel |

### Documents / Waivers

| Field | Notes |
|---|---|
| **Client Email** | |
| **Document Type** | waiver, health-questionnaire, contract or other |
| Signed Date | |
| Expiry Date | |
| Notes | |

## Dates

Dates are read the Australian way, day first:

- **03/04/2025**, **3/4/2025** and **3/4/25** are all 3 April 2025. You can use / - or . between the numbers.
- **2025-04-03** (YYYY-MM-DD) works too.
- A date with the month written out, like **3 April 2025**, is read as written.
- Two digit years up to this year are 2000s, later ones are 1900s, so a birthday of 15/6/90 is 1990.
- Real date cells in an Excel file come through correctly whatever format they show in.

If a date cannot be a real date (for example 31/02/2025) it is left empty.

## How statuses are read

The wizard looks for words in your status columns, so most systems' wording works:

| Your file says something like | Saved as |
|---|---|
| cancelled, cancel | Cancelled |
| inactive, suspended, frozen | Inactive |
| lead, prospect, trial | Lead |
| anything else, or blank | Active |

For payments: fail or declined is Failed, refund is Refunded, pending is Pending, anything else is Paid. Payment methods: cash; bank, EFT or transfer; card, credit, debit or Stripe; anything else is Other. For attendance: no or absent is No-show, late or cancel is Late cancel, anything else is Attended.

## Exporting from other systems

### PTminder

!steps
1. Log in to your PTminder account.
2. Go to **Reports** in the left sidebar.
3. Select **Client List** and download it as CSV.
4. Go to **Reports**, then **Payments**, and download as CSV.
5. Go to **Reports**, then **Attendance**, and download as CSV.
6. Upload each file separately, one import run per file. Use the **PTminder** type for the client list, **Payment History** for payments and **Attendance / Sessions** for attendance.

### ABC Trainerize

!steps
1. Log in to ABC Trainerize on the web (not the mobile app).
2. Open the **Clients** tab in the left-hand menu.
3. Select all clients, or tick just the ones you want to bring over.
4. Click the **Export** icon to download a CSV.
5. In Totality, open the ABC Trainerize guide on the Import screen and tap **Start Client Import**, then upload that CSV.

This export only includes first name, last name, email, phone and trainer name. It has no workout history, programmes or weight logs, and Trainerize does not offer a self-serve export of those. Keep your Trainerize account active, or ask their support for a manual export, if you need that history.

:::tip First and last name in separate columns?
Totality needs one Full Name column. In your spreadsheet, add a column with a formula like =A2&" "&B2 to join them, then map that column to Full Name.
:::

### Mindbody: members

!steps
1. Log in to Mindbody and open **Insights**, then **Reports**, from the left navigation.
2. Click the **Clients** category tile, then open **Mailing Lists**.
3. Change the report type dropdown to **Email List**. Do not use "Mailing List": it looks like the obvious choice but has no email addresses.
4. Click **Generate**, then the small **XLS** icon above the results to download it.
5. In Totality, tap **Start Client Import** in the Mindbody guide and upload the file as it is.

The Email List covers name, phone and email. It does not include membership status or start date. Those are optional, so the import still works. Fill them in per member afterwards, or ask Mindbody support about their paid export if you need them in bulk.

### Mindbody: payment history

!steps
1. In Mindbody, go to **Reports**, then **Sales**.
2. Filter by date range or location if you only want part of it.
3. Click **Export** to download the sales CSV.
4. In Totality, tap **Start Payment Import** in the Mindbody guide and upload the file. Mindbody's column names are not recognised automatically for this report, so match client email, date, amount and the rest yourself on the Map Columns step.

### Any other system

Most gym software can export a client list to CSV or Excel. Use the **Clients** type and match the columns. If your system only gives you a PDF or you are stuck, email the export to admintotality@gmail.com and we will help.

## Questions

?? My file has a column the wizard does not know. Will it break?
No. Columns you do not match are ignored.

?? Can I import a file with first and last names in separate columns?
Join them into one Full Name column first. See the tip above.

?? Do I need the Membership Status column?
No. Without it, members come in as active.
