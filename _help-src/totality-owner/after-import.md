---
title: After importing, and running alongside your old system
summary: What to check once your data is in, how your existing members get into the app, and how to move billing across without double charging anyone.
---

Your data is in. Before you tell members, run through this list, then plan how you move their payments across.

## Check list after an import

!steps
1. Open **Members**, then **Clients**. Check the count matches your old system and spot check a few members.
2. Tap a few members and check their **Date of Birth** and **Member Since** dates. If any look wrong, fix them with **Edit** on their profile. See [how dates are read](import-files.html#dates).
3. Use the trainer filter chips at the top of Clients to check each trainer has the right members. Use **Select**, then **Assign**, to fix any that were not matched. See [Members](members.html).
4. If you imported **Membership Types**, open **Sales**, then **Memberships**. Each one comes in switched on, with **Includes classes** off. Check the price and billing frequency, and turn **Includes classes** on for any that should cover classes.
5. If you imported **Attendance**, it shows in each member's **Membership, freeze and attendance** history.
6. If any rows failed, open the error report, fix those rows and import them again.

:::note Payment history and documents
Imported **Payment History** and **Documents / Waivers** are kept on file in Totality as a record. They do not appear in Revenue, Insights or the Compliance hub, which only show what happens in Totality from now on. Keep your original export as well.
:::

## How your existing members get in

Every member you imported was emailed an invite from your gym with their login details and a temporary password. When they first sign in, they are asked to set their own password.

- Tell members to look out for the email (and check spam).
- If someone lost theirs, they can use **Forgot Password?** on the sign in screen with the same email.
- Members who already had a Totality account (for example from another gym or a trainer) are not sent a new password. Add them with [Add client](add-members.html): they get an invite inside the app and join your gym when they tap **Accept**.

## Getting members onto Totality billing

The import does not move anyone's payments. Their direct debits or card subscriptions keep running in your old system until you stop them there. To move a member across without charging them twice:

!steps
1. [Connect Stripe](stripe-connect.html) and [create your memberships](memberships.html) in Totality.
2. Ask the member to add a card in the Totality app. From their profile you can tap **Request Payment Method** to send them a reminder. See [Client detail](client-detail.html).
3. Pick a changeover date, ideally the day after their last payment in the old system.
4. Cancel their billing in the old system.
5. Start their membership in Totality: **Memberships**, then **Members**, then **Add membership**. Their card is charged and billing continues on the frequency you set.

Members can also buy a membership themselves from your shop in the app. See [Marketplace and shop](marketplace.html).

## Running side by side

Many gyms run both systems for a few weeks. A simple way to do it:

- **Week 1:** import trainers and members, set up memberships, classes and PT packages. Trainers start using Totality for programmes and sessions.
- **Weeks 2 to 4:** move members' billing across in batches, on each member's next billing date. Take new sign-ups only in Totality.
- **When billing is all moved:** keep your old system read only until you no longer need its history, then close it.

:::tali
Do your trainers first. Once they're in, the members follow, and I can start flagging who's gone quiet. Easy as.
:::

## Questions

?? A member says they never got their invite.
Check the email address on their profile. Ask them to check spam, or to use **Forgot Password?** on the sign in screen with that email.

?? Can I re-send the invite?
There is no re-send button for imported members. **Forgot Password?** gives them a fresh way in. If that does not work, email admintotality@gmail.com.

?? Will members be charged twice?
Only if both systems are billing them at once. Cancel billing in the old system before you start their membership in Totality.

?? Can members keep their existing card details?
Card details cannot be moved from another system. Each member adds their card once in the Totality app.
