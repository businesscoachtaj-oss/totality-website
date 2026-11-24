---
title: Stripe Connect and payouts
summary: Connect your own Stripe account so members can pay you, and understand the platform fee.
---

Totality takes member payments through **Stripe**, a payments company used by millions of businesses. Your gym gets its own Stripe Express account. Members pay by card or straight from their bank account in the app, and the money goes to your Stripe balance and then to your bank.

You need Stripe connected before you can sell memberships, PT packages, paid classes, POS payment links, one-off charges or shop products.

## Connect Stripe

!steps
1. Tap the **Sales** tab. Until Stripe is set up, an orange **Connect Stripe to get paid** card sits at the top. Tap it, or tap **Stripe Connect setup**.
2. Read the **Connect your Stripe account** card and tap **Connect Stripe account**.
3. Stripe opens in your browser. Enter your business details, your ID and the bank account you want payouts to go to. Stripe checks these for you (this is called KYC).
4. When Stripe says you are done, come back to Totality.
5. Pull down on the Connect Stripe screen to refresh it.

!phones[Before you connect](img/stripe-connect-start.png)[Connected, with charges and payouts on](img/stripe-connect-done.png)

When everything is approved, the screen says **Stripe connected** with a green tick next to **Charges** and **Payouts**. The **Connect payments** step on your dashboard's setup card ticks itself off.

## If Stripe needs more details

If you left Stripe before finishing, the screen says **Onboarding in progress** and the button changes to **Complete Stripe setup**. Your dashboard shows **Finish your Stripe setup**. Tap the button to carry on where you left off. Payments and payouts start once Stripe has everything it needs.

## How members can pay

Under **How members can pay** on the Connect Stripe screen:

- **Card** is always on: Visa, Mastercard, Amex, Apple Pay and Google Pay. Stripe's fee is 1.65% + 30c.
- **Bank account (PayTo)** is on unless you switch it off. Members add their bank account under **Payments** in their app and approve it once in their banking app. Then memberships, PT packages, charges and bookings can come out of it by themselves. Stripe's fee is 1% + 30c, never more than A$3.50.

!phone[How members can pay](img/stripe-connect-how-members-pay.png)

The first time, Stripe has to switch bank payments on for your account. Under the switch it says **Stripe is checking this**, usually for a day or two, and members save a card instead until then. Once it reads **Ready. Stripe has switched bank payments on for your gym**, members can add a bank account. If Stripe needs more details, finish them in your Stripe account.

A bank payment takes about a minute to confirm. If the bank says no, the payment shows as failed and you get a notification, the same as a failed card.

## Your debit day

Every repeating payment comes out on the same day, for everyone, by card or bank. Under **Debit day**, pick:

- **Weekly and fortnightly**: a day of the week. Monday unless you change it.
- **Monthly**: a date from the 1st to the 28th. The 1st unless you change it.

!phone[Your debit day](img/stripe-connect-debit-day.png)

A member who joins between debit days pays a part payment for the days up to your debit day, then the full amount every debit day after. The grey box shows an example with real dates. Quarterly and yearly memberships start the day they're bought.

If you change the day, memberships and packages already running move to the new day at their next payment. The days in between are added to that payment, so nobody pays twice or misses a day.

## Managing payouts

Payout timing, your bank account and tax details are managed by Stripe. Use the Stripe Express dashboard at **dashboard.stripe.com** to see payouts, update your bank account or answer any Stripe questions.

## The platform fee

| | |
|---|---|
| Commission on your coaching or membership revenue | None |
| Platform fee on payments members make in the app | 1.25% |
| Who pays it | You, out of the payout. It is never added to what your member pays |
| Stripe fees | 1.65% + 30c for Australian cards, or 1% + 30c (never more than A$3.50) for bank account payments, charged by Stripe as normal. On POS and shop sales Totality pays Stripe and adds it to the platform fee, so the total is the same |

The fee applies to memberships, PT packages, paid class bookings, POS payment links, one-off charges and shop sales. Payouts, net of the fee, go straight to your bank.

:::note Your Totality subscription is separate
What you pay Totality for your plan is billed to your own card. It has nothing to do with your Stripe Connect account. See [Your Totality plan](your-plan.html).
:::

## Questions

?? How long does Stripe take to approve me?
Often a few minutes. If Stripe needs extra documents it can take longer, and Stripe will email you.

?? When does money reach my bank?
On Stripe's payout schedule for your account. You can see and change it in the Stripe Express dashboard.

?? Can I use the Stripe account I already have?
Totality creates a new Stripe Express account for your gym, connected to Totality. You sign in to it with your email. Your old Stripe account and its customers are not moved across.

?? Do my members need a Stripe account?
No. They just add a card or a bank account in the Totality app.

?? Can I turn bank payments off?
Yes. Switch off **Bank account (PayTo)** under How members can pay. Members can't add a new bank account, and checkout in your shop and payment links is card only. A bank account a member already saved can still be charged.

?? Is there a limit on bank payments?
A member's bank agreement allows up to A$1,500 a payment. Anything bigger needs a card.

?? Why does revenue in Totality look lower than the amount charged?
Totality shows what you actually receive, after the platform fee. See [Revenue and insights](revenue-insights.html).
