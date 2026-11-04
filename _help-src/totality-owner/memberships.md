---
title: Memberships
summary: Create your membership options, start a member on one, see who is on what, and cancel at the end of a billing period.
---

**Memberships** is where you set up what you sell (Unlimited, Off Peak, 12 Month Upfront and so on) and where you see who is paying for which one. Members pay by card through your [Stripe account](stripe-connect.html), so connect Stripe first.

Open the **Sales** tab, then **Memberships**. There are two tabs: **Products** and **Members**.

!phones[Your membership options](img/memberships-products.png)[Who is on each one](img/memberships-members.png)

## Create a membership

!steps
1. On the **Products** tab, tap **+ New**.
2. Fill in **Name** (for example Full Access) and an optional **Description** ("What's included?").
3. Enter the **Price ($)**.
4. Pick the **Billing frequency**: **Weekly**, **Fortnightly**, **Monthly**, **Quarterly** or **Yearly**.
5. Turn on **Includes classes** if members on this membership book classes for free. See [Classes](classes.html#who-pays-for-a-class).
6. Leave **Active** on so it can be sold.
7. Tap **Create product**.

!phone[A new membership](img/memberships-new.png)

Each membership shows its price and frequency (for example $29.00 AUD/wk) and a **Classes** pill if it includes classes. Use the switch to make it active or inactive. Tap one to edit it.

Active memberships also appear in your gym's shop, where members can buy them themselves. See [Marketplace and shop](marketplace.html).

## Start a member on a membership

The member needs a card saved with your gym first. If they do not have one, ask them to add one (see [Ask a member to add a card](#ask-a-member-to-add-a-card)).

!steps
1. Open the **Members** tab and tap **+ New** (or **Add membership**).
2. Pick the **Client**.
3. Pick the **Membership plan**.
4. Optional: turn on **Custom amount** ("Override the plan price with a custom amount") to charge a different price, then enter the **Amount ($)** and frequency.
5. Tap **Create subscription**.

Their default saved card is charged straight away, and then again on each billing date. If anything fails you will see "Could not create subscription" with the reason.

## The Members tab

Each row shows the member, their membership and price, their **Next bill** date and a status:

| Status | Meaning |
|---|---|
| Active | Paying as normal |
| Past due | The last payment failed. See [Failed payments](failed-payments.html) |
| Paused | Paused, for example by a freeze. See [Check-in and freezes](check-in-freezes.html) |
| Cancelled | Ended |

## Ask a member to add a card

If a member on the **Members** tab has no card saved, you can email them a link to add one.

!steps
1. On the **Members** tab, find the member's row.
2. Tap **Ask to add card**. It shows "Sending..." while it works.
3. You see **Request sent**: "We emailed (their name) a link to add a card." If it could not send, you see **Could not send** with the reason.

The email comes from your gym and links to the page where they add their card in Totality. You can also ask from the member's page. See [Failed payments and cards](failed-payments.html#ask-a-member-to-add-a-card).

## Cancel a membership

!steps
1. On the **Members** tab, tap the member's row.
2. The message says "The client will keep access until the end of the current billing period."
3. Tap **Cancel at period end**, or **Keep active** to leave it.

No more payments are taken after the current period ends. Members can also cancel their own membership from their app, at the end of the period they have paid for.

## Questions

?? Can I change the price of a membership people are already on?
To change what an existing member pays, cancel their membership at the end of the period and start them again on the new one, or with a **Custom amount**.

?? Can I offer a one-off pass, like a 10 visit pass?
Memberships repeat. For a one-off sale, create a product in [Products](marketplace.html) with **One-off** billing, or use [Charge a member](charges-pos.html).

?? Can I pause a membership for an injury or holiday?
Yes, with a freeze. See [Check-in and freezes](check-in-freezes.html).

?? What is the difference between Memberships and PT packages?
Memberships are for using the gym (and classes, if included). [PT packages](pt-packages.html) are for 1:1 sessions with a trainer and give weekly session credits.
