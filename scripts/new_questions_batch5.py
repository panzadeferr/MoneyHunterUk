"""Batch 5: stacking and cashback questions, from the guides added in add_stacking_guides.py.
Run: python3 scripts/new_questions_batch5.py && python3 scripts/sync_qbank.py"""
import json,os,random,re,difflib
base=os.path.join(os.path.dirname(__file__),"..","data","questions")
R="2027-05-01"
def Q(topic,d,question,options,answer,expl,learn,vol=None):
    return dict(topic=topic,d=d,question=question,options=options,answer=answer,expl=expl,learn=learn,vol=vol)
S=[
Q("cashback",1,"What does 'stacking' mean?",["Getting more than one saving on the same purchase","Buying lots of the same item","Saving cash in a pile"],0,"Stacking combines separate layers of saving, such as a sale price, cashback and loyalty points, on one purchase.","pb-cb-stacking-basics"),
Q("cashback",2,"You use a voucher code that the cashback site does not list. What often happens?",["The cashback is declined","The cashback doubles","Nothing"],0,"Many cashback sites decline cashback when you use an unlisted voucher code, so check the shop's terms first.","pb-cb-stacking-basics"),
Q("cashback",2,"A cashback credit card stacks with a cashback site because…",["The card is only how you pay","Cards pay the site","They are the same thing"],0,"The cashback site tracks your click, and the card is just the payment method, so the two usually work together.","pb-cb-stacking-basics"),
Q("cashback",1,"You buy a £40 item you didn't need, with 10% cashback. What have you done?",["Saved £40","Spent £36 net on something you didn't need","Made £4 profit"],1,"Cashback only helps on things you would have bought anyway. Otherwise you have just spent money.","pb-cb-not-worth"),
Q("cashback",1,"What should you do before you click through to a shop from a cashback site?",["Start with an empty basket and one shop tab","Open five shop tabs","Turn on a VPN"],0,"TopCashback says an empty basket, one shop tab and no VPN or ad blocker give the best chance of tracking.","pb-cb-order"),
Q("cashback",2,"You place two separate orders from one cashback click. What is the risk?",["The second order may not track","Both orders double","Nothing"],0,"Each order needs its own click through the cashback site.","pb-cb-order"),
Q("cashback",2,"Two cashback or voucher browser extensions are active together. What can happen?",["One overrides the other and cashback is lost","They add together","Prices drop"],0,"Use one at a time. Competing extensions can overwrite the click that your cashback depends on.","pb-cb-order"),
Q("cashback",2,"Quidco says to raise a missing cashback claim within how many days of purchase?",["45 days","7 days","1 year"],0,"Quidco's help page says to raise a claim within 45 days of purchase, and after at least 72 hours. Check the current page.","pb-cb-missing",R),
Q("cashback",2,"What do you need to raise a missing cashback claim?",["Your order confirmation or receipt","Your bank PIN","A friend's reference"],0,"A screenshot of the confirmation with the shop, order reference, date and total is what the claim form asks for.","pb-cb-missing"),
Q("cashback",1,"Cashback shows as 'pending'. How should you treat it?",["Don't count it until it is paid","Spend it now","Ignore it forever"],0,"Pending cashback can be declined or delayed. Count it only once it has landed.","pb-cb-missing"),
Q("cashback",2,"You return a cashback purchase. What usually happens to the cashback?",["It is declined or reversed","You keep it","It doubles"],0,"Returns and cancellations normally cancel the cashback on that order.","pb-cb-missing"),
Q("cashback",2,"You carry a balance on a cashback credit card. What often happens to the reward?",["Interest wipes it out","It grows","Nothing"],0,"Reward cards often charge higher rates, so interest can cost more than you earn.","pb-cb-cards"),
Q("cashback",1,"What is the safe way to use a cashback credit card?",["Set a Direct Debit for the full balance","Pay the minimum","Take out cash with it"],0,"Clear it in full every month and use it only for normal spending, never for cash withdrawals.","pb-cb-cards"),
Q("cashback",2,"Section 75 on a credit card covers items priced…",["Over £100 and up to £30,000","Under £100","Any price"],0,"The limit is per item. A part-payment on the card can bring the whole cost under cover.","pb-cb-cards"),
Q("cashback",2,"You see a 1% cashback card with a spending cap and a rate that drops after a year. Check…",["The terms before relying on the headline rate","Nothing, it is fixed","Only the colour"],0,"Introductory rates and caps change, so read the current terms.","pb-cb-cards",R),
Q("cashback",2,"A retailer enters administration. What may happen to your gift card?",["It may stop being accepted or only cover part of an order","It doubles","It is refunded automatically"],0,"Administrators can stop accepting gift cards or limit them, so spend the balance quickly.","pb-cb-giftcards"),
Q("cashback",2,"You paid for a gift card by credit card, and the retailer fails. What may help?",["A Section 75 claim with your card provider","Nothing","A phone call to the shop"],0,"You may be able to claim from your card provider, depending on the item price and the circumstances.","pb-cb-giftcards"),
Q("cashback",1,"Which test should you use before stacking?",["Would I buy this anyway?","Is it the biggest discount?","Is it on social media?"],0,"If you would not buy it anyway, no amount of stacking makes it a saving.","pb-cb-not-worth"),
]
# assign ids, shuffle options, drop near-duplicates of existing questions
pref={"cashback":"cb"}
files={}
for t in pref:
    p=os.path.join(base,t+".json");files[t]=json.load(open(p))
existing=[q for d in files.values() for q in d["questions"]]
alltext=[]
for f in os.listdir(base):
    if f.endswith(".json") and f not in("index.json","investigations.json"):
        alltext+=[q["question"].lower() for q in json.load(open(os.path.join(base,f)))["questions"]]
def nextnum(t):
    nums=[int(re.search(r"-(\d+)$",q["id"]).group(1)) for q in files[t]["questions"] if q["id"].startswith(pref[t]+"-")]
    return max(nums or [0])+1
added=0;skipped=[]
for s in S:
    t=s["topic"]
    if any(difflib.SequenceMatcher(None,s["question"].lower(),x).ratio()>0.72 for x in alltext):skipped.append(s["question"][:50]);continue
    qid=f"{pref[t]}-{nextnum(t):03d}"
    opts=list(s["options"]);correct=opts[s["answer"]];random.Random(qid).shuffle(opts)
    o={"id":qid,"topic":t,"difficulty":s["d"],"type":"mc","question":s["question"],"options":opts,"answer":opts.index(correct),"explanation":s["expl"],"learn_more":s["learn"]}
    if s["vol"]:o.update({"volatile":True,"review_by":s["vol"],"verify":s["learn"]})
    files[t]["questions"].append(o);alltext.append(s["question"].lower());added+=1
for t,d in files.items():open(os.path.join(base,t+".json"),"w").write(json.dumps(d))
print("added",added,"skipped as duplicates:",len(skipped));print(*skipped,sep="\n")
