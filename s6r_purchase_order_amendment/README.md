Scalizer Purchase - Order Amendment
====================================

This module tracks amendments ("avenants") linked to a purchase order.

## Overview

When a vendor bill exceeds the remaining amount to invoice on a purchase order, a
common practice is to create an **amendment**: a new purchase order covering the
gap, linked to the origin order. Odoo standard offers no way to trace this link
in either direction.

This module adds that traceability and a manual action to create an amendment
from a confirmed purchase order. It does **not** compute the invoicing gap nor
create the amendment automatically when a vendor bill is validated — the
amendment creation stays a manual, explicit user action.

## Features

- `Create Amendment` button on a confirmed purchase order (`state = 'purchase'`)
  that is not itself an amendment
- The new order is a duplicate of the origin order, linked back to it
- The amendment name is suffixed with the origin order name
  (`{origin_name}/AMDT-01`, `{origin_name}/AMDT-02`, ...)
- `Amendments` smart button on the origin order to browse its linked amendments

## Usage

1. Open a confirmed purchase order.
2. Click **Create Amendment**.
3. The new amendment order opens in form view, linked to the origin order
   through the `Amendment Of` field.
4. From the origin order, use the **Amendments** smart button to list all its
   amendments.

## Technical Notes

- An amendment cannot itself be amended: the button is only available on
  non-amendment orders (`amendment_of_id` empty).
- The amendment suffix index is based on the number of existing amendments of
  the origin order (`len(amendment_ids) + 1`), not on a dedicated `ir.sequence`.
- Amendments remain independent `purchase.order` records: their amounts are not
  automatically consolidated with the origin order in standard reports.

## Authors

* Scalizer

## Maintainers

This module is maintained by [Scalizer](https://www.scalizer.fr).

![Scalizer](./static/description/logo.png)
