"""Adds the stacking guides to the cashback chapter and expands the gift card guide. Idempotent."""
import json,os
p=os.path.join(os.path.dirname(__file__),"..","data","playbook.json")
d=json.load(open(p))
ch=[c for c in d["chapters"] if c["id"]=="cashback"][0]
D="2026-10-15"
def A(id,title,summary,mins,body,sources):
    return {"id":id,"title":title,"summary":summary,"existing_guide":None,"status":"written","read_minutes":mins,"reviewed":D,"body":body,"sources":sources,"question_count":0}
p_=lambda t:{"type":"p","text":t}
h=lambda t:{"type":"h","text":t}
lst=lambda *i:{"type":"list","items":list(i)}
stp=lambda *i:{"type":"steps","items":list(i)}
warn=lambda t:{"type":"warn","text":t}
tip=lambda t:{"type":"tip","text":t}
key=lambda *i:{"type":"key","items":list(i)}

new=[
A("pb-cb-stacking-basics","How stacking works","The layers you can combine on one purchase, and which ones usually clash.",5,[
 p_("Stacking means getting more than one saving on the same purchase. Each saving is a separate layer, and the skill is knowing which layers work together."),
 h("The layers"),
 lst("A sale price or a voucher code from the shop.","Cashback from a cashback site, paid on top of what you pay.","A discounted gift card or a gift card app that pays cashback.","A rewards or cashback credit card.","The shop's own loyalty points."),
 h("What usually works"),
 lst("Loyalty points plus cashback, if the cashback site allows it for that shop.","A cashback credit card on top of cashback from a site, because the card is only the payment method.","A gift card bought at a discount, then spent at the shop."),
 h("What usually clashes"),
 lst("A voucher code the cashback site doesn't list: many sites decline cashback when you use one.","Gift cards as payment: many shops are excluded from cashback when you pay with one, so read the shop's terms on the cashback site.","Browser extensions that compete: use only one at a time."),
 key("Every layer has its own terms. Check the shop's terms on the cashback site before you pay.","Order matters: see the next guide."),
 warn("Stacking is not worth it if it makes you buy something you wouldn't have bought. 10% back on a purchase you didn't need is still 90% spent."),
],["https://www.topcashback.co.uk/help/why-didnt-my-purchase-track/","https://support.quidco.com/en/articles/4127319-why-can-t-i-raise-a-cashback-claim"]),

A("pb-cb-order","Stacking in the right order","What to click, and when, so your cashback actually tracks.",4,[
 p_("Most stacking mistakes come from doing things in the wrong order. This is the routine TopCashback and Quidco describe in their own help pages."),
 stp("Decide what you're buying and whether you'd buy it anyway.","Compare prices first, then do the rest of the steps below. Comparison sites visited after your click can break tracking.","Open the cashback site, or its app or extension, and check the shop's terms: rate, exclusions, and whether gift cards or voucher codes are allowed.","Start with an empty basket and one shop tab open.","Click through from the cashback site, then buy in the same session.","Pay with the card you chose, and keep the order confirmation."),
 h("Things that break tracking"),
 lst("VPNs, ad blockers and privacy software.","Two cashback or voucher extensions at once.","Clicking through too early, then browsing other sites.","Several shop tabs open at once.","Reusing one click for a second order: each order needs its own click."),
 tip("TopCashback says that if your cashback hasn't tracked after 7 days, you can lodge a missing cashback claim. Check the current guidance on their help page."),
 warn("Help pages change. Treat this as a checklist and check the cashback site's own page for the shop before you buy."),
],["https://www.topcashback.co.uk/help/why-didnt-my-purchase-track/","https://www.quidco.com/article/make-a-claim/"]),

A("pb-cb-missing","When cashback goes missing","Pending, declined, and how to raise a missing cashback claim.",5,[
 p_("Cashback does not always track, and it can be declined. Knowing the time limits is what separates a recovered claim from a lost one."),
 h("What the sites say (checked 15 October 2026)"),
 lst("Quidco: raise a missing cashback claim within 45 days of the purchase, and wait at least 72 hours after buying first. You need a record of your click-through, and some retailers don't accept claims at all.","Quidco Compare deals can take up to 120 days to track, and claims can't be raised on them.","TopCashback: most retailers accept claims for around 100 days from the purchase, and the exact window is in the retailer's terms on the offer page."),
 h("What to keep"),
 lst("A screenshot of the order confirmation or receipt.","The shop name, order reference, date, time and total.","What you bought, how you paid, and any codes or fees."),
 h("Why a claim can be stopped"),
 lst("The shop doesn't accept manual claims.","A voucher, payment method or item wasn't eligible.","The order was returned or cancelled."),
 warn("These time limits come from the sites and can change. Check the shop's page on the cashback site, and don't wait until the end of a window."),
 tip("Add the expected payout date to the Progress tracker, so you notice when something is overdue."),
],["https://www.quidco.com/article/make-a-claim/","https://support.quidco.com/en/articles/4127319-why-can-t-i-raise-a-cashback-claim","https://www.topcashback.co.uk/help/lodge-a-missing-cashback-claim/"]),

A("pb-cb-cards","Cashback credit cards","Why the reward only works if you clear the balance every month.",4,[
 p_("A cashback credit card pays you a small percentage of what you spend. It can stack with cashback sites, because the card is only how you pay."),
 h("Who it suits"),
 p_("Only people who clear the balance in full every month. MoneySavingExpert's guide warns that interest wipes out the rewards if you don't, and that reward cards often charge higher rates than standard cards."),
 h("What to check before applying"),
 lst("The annual fee, if any.","Spending caps and how long an introductory rate lasts, since many rates drop after a period.","The rate on each type of spending.","Whether you'll use it only for normal spending, never for cash withdrawals or spreading payments."),
 h("Setting it up safely"),
 stp("Set up a Direct Debit for the full balance.","Use the card for spending you were already doing.","Check the statement each month, then repeat."),
 h("A bonus: Section 75"),
 p_("For an item priced over £100 and up to £30,000, a credit card can give extra protection if the seller fails. It applies per item, and usually doesn't work for third-party sellers or when you pay through some wallets. A part-payment on the card can bring the whole cost under cover."),
 warn("Every credit application leaves a mark on your credit file. Apply only for a card you want to keep using."),
],["https://www.moneysavingexpert.com/cards/cashback-credit-cards","https://www.experian.co.uk/consumer/credit-cards/guides/section-75-protection.html"]),

A("pb-cb-not-worth","When stacking isn't worth it","The traps: tiny payouts, time cost, and spending to save.",4,[
 p_("Stacking is a way to make planned spending cheaper. It stops being worth it in a few common situations."),
 h("Watch for"),
 lst("Buying something you didn't need, because there was a deal.","Spending an hour to save a pound or two.","Minimum payout limits that leave small balances stuck.","Cashback that never gets confirmed, because you counted it before it was paid.","Using credit you can't clear in full, which costs more than you earn.","Applying for lots of products, which can leave marks on your credit file."),
 h("A quick test"),
 key("Would I buy this anyway? If not, stop.","How long will it take, and what is my time worth?","Can I pay it off in full this month?"),
 tip("Count cashback as a bonus only when it has landed in your account. The Progress tracker can show you what is pending and what is paid."),
 warn("Anyone who tells you that you can get rich from cashback is selling something. For most people it's a modest saving on planned purchases."),
],["https://www.moneysavingexpert.com/cards/cashback-credit-cards","https://www.quidco.com/article/make-a-claim/"]),
]
have={a["id"] for a in ch["articles"]}
for a in new:
    if a["id"] not in have: ch["articles"].append(a)
# expand gift cards guide
g=[a for a in ch["articles"] if a["id"]=="pb-cb-giftcards"][0]
if not any(b.get("text","").startswith("Which? found") for b in g["body"]):
    i=[k for k,b in enumerate(g["body"]) if b.get("type")=="warn"][0]
    g["body"][i:i]=[
     {"type":"h","text":"What can go wrong"},
     {"type":"list","items":["If a retailer goes into administration, it can stop accepting gift cards or limit how much of an order they cover.","Cards often expire one to two years after purchase, and some charge inactivity fees. Read the terms.","Which? found in 2021 that 38% of people holding vouchers for failed retailers couldn't spend the full balance (survey from October 2021, so check current terms)."]},
     {"type":"tip","text":"If a retailer looks to be in trouble, spend the card quickly. If you paid by credit card, you may be able to make a Section 75 claim with your card provider."}]
    g["sources"]=list(dict.fromkeys(g["sources"]+["https://www.which.co.uk/news/article/gift-card-warning-avoid-getting-stuck-with-a-worthless-voucher-this-christmas-aOCFy2W2QVWx"]))
    g["reviewed"]=D
d["updated"]=D
open(p,"w").write(json.dumps(d,indent=2,ensure_ascii=False)+"\n")
print("articles in cashback:",len(ch["articles"]))
