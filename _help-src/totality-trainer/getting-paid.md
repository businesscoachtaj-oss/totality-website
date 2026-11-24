---
title: Getting paid
summary: How money reaches you with the POS add-on and Stripe Connect, the platform fee, and how it works for gym trainers.
---

Totality can take payments from your clients: one-off payment links, cards on file, and products in your shop. How it works depends on whether you're independent or at a gym.

## Independent trainers: POS add-on and Stripe

[[POS]]
Payments go through **Stripe** into your own bank account. You need two things:

1. **The POS add-on** (A$9.99 a month, or in a bundle). It needs a Solo plan.
2. **Trainer Payouts** set up, which connects your bank through Stripe Connect.

!steps
1. Go to **Settings > Manage Subscription** (or **Settings > Stripe Payouts**).
2. On the **POS add-on** card, tap **Add POS, $9.99/mo** and pay in Stripe.
3. Back in Totality, scroll to **Trainer Payouts** and tap **Set Up Payouts**.
4. Stripe asks for your business details, ID and bank account. Finish every step.
5. While Stripe checks your details the status reads **Verification in progress** ("This usually takes 1-2 business days"). Then it reads **Payouts active**.

!phones[The POS add-on](img/plans-solo-addons.png)[Trainer Payouts with payouts active](img/getting-paid-payouts.png)

The button under Trainer Payouts changes with your status:

| Status | Button |
|---|---|
| Not set up | **Set Up Payouts** |
| Verification in progress | **Continue Setup** |
| Account restricted (Stripe needs something) | **Fix Issues** |
| Payouts active | **View Connect Dashboard** |

If you tap **Set Up Payouts** without the POS add-on, Totality asks **POS Add-on Required** and offers **Purchase POS Add-on**.

## The platform fee

A 1.25% platform fee applies to payments your clients make in the app: PT packages, plans, one-off charges, payment links and shop sales. It comes out of your payout before it lands in your bank, and it is never added to what your client pays. It is not a commission on your coaching income. Stripe's own fee also comes out of your payout: 1.65% + 30c for Australian cards, or 1% + 30c (never more than A$3.50) for bank account payments. If you refund a payment, the matching share of the platform fee goes back to you. Your Totality plan itself isn't affected.

## How clients can pay: card or bank account

Under Trainer Payouts, **How clients can pay** shows two ways:

- **Card** is always on: Visa, Mastercard, Amex, Apple Pay and Google Pay.
- **Bank account (PayTo)** is on unless you switch it off. Clients can pick **Bank account** when they pay through your shop, a payment link or Discover, and save a bank account with you under **Payments**. They approve a PayTo agreement in their own banking app once, then payments come straight out of that account. Stripe's fee is 1% + 30c, never more than A$3.50, which is a lot less than a card on bigger amounts.

A bank payment takes about a minute to confirm. If the bank says no, you get a notification.

:::note Bank payments switch on after Stripe checks
The first time, Stripe has to switch bank payments on for your account. Under the switch it says **Stripe is checking this**, usually for a day or two, and clients save a card instead until then. Once it reads **Ready**, bank payments are on. If it asks for more details, open your Stripe account from Payments and finish them.
:::

## Your debit day

Every repeating payment (memberships and PT packages that repeat) comes out on the same day, for everyone, by card or bank. You pick it once:

- **Weekly and fortnightly**: a day of the week. Monday unless you change it.
- **Monthly**: a date from the 1st to the 28th. The 1st unless you change it.

Someone who starts between debit days pays a part payment now for the days up to your debit day, then the full amount every time after. The box under the drop downs shows an example with real dates. If you change the day, plans already running move to the new day at their next payment, and nobody pays twice or misses a day.

!phone[How clients can pay and your debit day](img/getting-paid-debit-day.png)

## What you can do once it's on

- **[Payment links](payment-links.html)**: charge any amount for anything, and send the link by SMS, email or copy.
- **Cards and bank accounts on file**: request or add a client's card from their profile, or ask them to add a bank account under Payments. See [Client profile](client-profile.html#payment).
- **[Plans for clients](client-plans.html)**: put a client on a membership or a PT package that repeats, from their page.
- **[Your shop](marketplace.html)**: sell programmes, PT packages, memberships and anything else.
- **Revenue** on Home: this month's earnings, from Stripe. See [Marketplace and revenue](marketplace.html#revenue).

## Trainers at a gym

At a gym, payments go to the **gym's** Stripe account, not to you. You can still take payments with POS when the gym has POS (Studio, Club and Enterprise include it). The POS screen reminds you: "Payments you take here go to your gym's account, not to you." How you're paid by the gym is between you and the gym.

You don't need the POS add-on or your own Stripe account at a gym.

## Questions

?? When does Stripe pay me?
Stripe pays out to your bank on its normal schedule for your account. Check it in **View Connect Dashboard**.

?? I'm on Free. Can I take payments?
No. The POS add-on needs a Solo plan. You can still record sessions a client paid for in cash or by bank transfer with **Add sessions**. See [Sessions left](credits.html).

?? Can I use my existing Stripe account?
**Set Up Payouts** walks you through Stripe's own sign-up for a connected account. Follow the steps Stripe shows you there.

?? Can a client pay by bank account without saving it?
Yes. In your shop, a payment link or Discover they can pick **Bank account** at checkout and approve it in their banking app. Saving it under Payments is only needed when you put them on a plan from their page.

?? Who handles refunds?
There's no refund button in the Totality app. Email admintotality@gmail.com with the client, amount and date, and the team will help.

## Disputed payments

A dispute is when a client asks their bank to reverse a card payment. If it happens you get a push notification and an email, and the payment is listed under **Disputed payments**, linked from the bottom of your POS screen under Recent charges.

!phone[Disputed payments for an independent trainer](img/getting-paid-disputes.png)

Each one shows who it was, how much, what the bank was told and the bank's deadline. Tap **Email us your side** and send anything that shows the payment was genuine. We answer the bank for you. While the bank decides, Stripe holds the disputed amount and its dispute fee from your Stripe balance. If the bank sides with you, the amount comes back.

