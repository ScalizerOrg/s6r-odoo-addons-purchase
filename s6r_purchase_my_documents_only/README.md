Scalizer Purchase - My Documents Only
=====================================

This module introduces a dedicated purchase security group that restricts users to their
own purchase documents and related records.

## Overview

The module is designed for users who must work in the **Purchase** application but should
only access the documents assigned to them.

It provides a dedicated group called **User: My Documents Only** and applies specific
access rights and record rules so that users can work only on their own purchasing data.

The module covers the following business scope:

- Requests for Quotation
- Purchase Orders
- Purchase Agreements
- Purchase Order Lines
- Purchase Agreement Lines
- Related Receipts
- Related Vendor Bills and Vendor Credit Notes

For vendor bills, access is granted when:

- the user is the **Bill Recipient / Buyer** on the bill (`invoice_user_id`)
- or the bill is linked to a purchase document owned by the user

This avoids missing invoices in cases where the bill buyer is not the original purchase
buyer, or the opposite.

## Features

- Adds a dedicated security group for restricted purchase users
- Gives access only to the user's own purchase documents
- Allows access to purchase documents without buyer when `user_id` is empty
- Restricts access to related receipts
- Restricts access to related vendor bills and vendor credit notes
- Keeps purchase administrators and standard purchase users unchanged
- Can expose the Purchase menus to the restricted group without granting standard purchase
  user rights
- Supports a dedicated Purchase dashboard section if configured

## Security Behavior

### Access Rights

The module gives the restricted group controlled access on the required models.

Main rules:

- **Purchase Orders**: read, write, create, no delete
- **Purchase Order Lines**: read, write, create, delete
- **Purchase Agreements**: read, write, create, no delete
- **Purchase Agreement Lines**: read, write, create, delete
- **Products / Vendors / Taxes / Currencies / UoM / Picking Types / Locations**: read only
- **Vendor Bills**: read, write, create, no delete
- **Vendor Bill Lines**: read, write, create, delete
- **Partial Reconciliations**: read only

### Record Rules

The restricted group can only access the following records:

- **Purchase Orders** where:
    - `user_id = current user`
    - or `user_id` is empty

- **Purchase Order Lines** linked to those purchase orders

- **Purchase Agreements** where:
    - `user_id = current user`
    - or `user_id` is empty

- **Purchase Agreement Lines** linked to those agreements

- **Receipts** linked to purchase orders owned by the current user
    - or purchase orders without buyer

- **Vendor Bills / Vendor Credit Notes** where:
    - the bill buyer is the current user
    - or the bill contains invoice lines linked to purchase order lines belonging to the
      current user

## Usage

1. Install the module.
2. Assign the **Purchases: My Documents Only** group to the target internal users.
3. Make sure these users do **not** inherit the standard broader purchase groups unless
   intentionally required.
4. Open the **Purchase** application.

The user will then be able to work only on:

- their own purchase orders
- their own purchase agreements
- their related receipts
- their related vendor bills

## Important Notes

- This module is intended for **internal users**.
- It is recommended to keep the standard Odoo multi-company security rules unchanged.
- Additional multi-company rules are usually not required unless custom models or custom
  cross-company behaviors are introduced.
- Vendor bill security must rely on stored relational paths and should not use non-stored
  fields in record rules.

## Technical Notes

The module is based on:

- custom access rights
- custom record rules
- menu group extension
- optional dashboard reassignment

Special care must be taken on vendor bill rules to avoid using non-stored fields in
domains.

## Authors

* Scalizer

## Contributors

* Houda BENTALEB

## Maintainers

This module is maintained by [Scalizer](https://www.scalizer.fr).

![Scalizer](./static/description/logo.png)
