---
title: Troubleshooting
summary: Fixes for the most common problems, from a screen that will not load to payments, invites, imports and locked features.
---

Start here when something is not working. Most problems are fixed by one of the first two steps.

## First, try these

!steps
1. **Refresh.** Pull down on the screen. On the web, reload the page.
2. **Update the app.** Close Totality fully (swipe it away), then open it again. Updates arrive this way. A fresh install also needs one close and reopen.
3. **Check your connection.** Many screens show "Could not load ... Check your connection and try again" with a **Try again** button.
4. **Sign out and back in.** Settings, then **Sign out**.

If it still does not work, tap the purple **?** button on any screen to report it, with what you tapped and what happened. Or email admintotality@gmail.com.

## Account and access

?? Every screen says "Your free trial has ended".
Your trial is over and no plan is active. Tap **Choose a plan** and subscribe. Your data is all still there. See [Your Totality plan](your-plan.html).

?? It says "Your account is locked".
The Totality team has locked the account. Your data is safe. Email admintotality@gmail.com.

?? A row has a "Locked" pill.
That feature is not on your current plan, or you have reached a limit. Tap it to see why, and **See plans and add-ons** to change plan.

?? The dashboard says "No gym assigned".
Your login is not linked to a gym. This can happen if you chose Solo Trainer at sign up, or the gym was set up by someone else. Email admintotality@gmail.com.

?? A change to my plan has not shown up.
Pull down to refresh, or close and reopen the app. Plan changes can take a minute to come through from Stripe.

## Payments

?? Members cannot pay / memberships will not start.
Check [Stripe is connected](stripe-connect.html) and shows green ticks for **Charges** and **Payouts**. Then check the member has a card on file: their page shows **Card on file** or **No payment method**.

?? "Needs client approval" when I charge a member.
Their bank wants them to approve the payment, which cannot be done on your device. Send a [POS payment link](charges-pos.html) instead so they can pay on their own phone.

?? A payment failed.
Open **Failed payments**, tap **Send update card link**, then **Retry** once they have updated their card. See [Failed payments and cards](failed-payments.html).

?? Revenue says "Connect Stripe to see revenue".
Stripe is not connected or not finished. Open **Sales**, then **Stripe Connect setup**.

## Members and trainers

?? Someone never got their invite email.
Ask them to check spam. They can use **Forgot Password?** on the sign in screen with the email you used. If they already had a Totality account, they need to accept your invite at the top of their app instead.

?? I cannot add a new member.
You may be at your plan's member limit. The dashboard shows "Member limit reached". Make someone inactive or move up a plan.

?? A trainer cannot see a member.
Trainers see their own clients in full. Assign the member to them from **Clients** (Select, then Assign) or **Reassign Trainer** on the member's page.

## Classes and sessions

?? A member says they cannot book a class.
Check the class is **Active** and has a scheduled session, the session is not full (they can join the waitlist), their membership is not frozen, and they have a card on file if the class has a casual price.

?? A session will not cash off.
The member has no unused credit with that trainer. See [PT packages and credits](pt-packages.html).

?? Payroll is missing sessions.
Only completed sessions and classes count. Settle pending sessions on the [gym schedule](gym-schedule.html) and mark classes **Complete**.

## Import

?? My dates came in wrong.
Day and month were swapped. Fix them on the member's page, and use YYYY-MM-DD in your file next time. See [File formats and columns](import-files.html#dates).

?? Rows were skipped.
They had no name, or no valid email. Fix them in your spreadsheet and import those rows again.

?? Members were not linked to their trainer.
The trainer must be in your gym before the import, and the name in your file must match their full name or email exactly. Use Select, then Assign, on Clients to fix them.

## Notifications

?? I'm not getting push notifications.
Push only works in the phone app, not the website. Check **Push notifications** is on in Settings, that your phone allows notifications for Totality, and that quiet hours are not holding them.

## Questions

?? How do I report a bug?
Tap the purple **?** button on the screen where it happened. Give it a short **Title**, describe what you did and what happened in **Description**, pick a **Priority** and tap **Submit**.

?? How fast will I hear back?
A real person reads every report and email. Mark it **urgent** if your gym cannot take payments or check members in.
