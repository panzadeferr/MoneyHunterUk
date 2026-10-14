"""Batch 3 questions, each written from the reviewed playbook guide named in learn_more.
Run: python3 scripts/new_questions_batch3.py   (appends to data/questions/*.json, skips existing ids)"""
import json,os
R="2027-05-01"
import random
def q(id,topic,d,question,options,answer,expl,learn,volatile=None,verify=None,review_by=None):
    correct=options[answer];options=list(options);random.Random(id).shuffle(options);answer=options.index(correct)
    o={"id":id,"topic":topic,"difficulty":d,"type":"mc","question":question,"options":options,"answer":answer,"explanation":expl,"learn_more":learn}
    if volatile:o.update({"volatile":True,"review_by":review_by or R,"verify":verify})
    return o
RR="pb-rent-rights";RD="pb-rent-deposits-fees";RP="pb-rent-paying";RC="pb-rent-credit-file";RW="pb-rent-rewards";RK="pb-rent-card"
ren=[
q("rent-001","renting",1,"Since 1 May 2026, can a landlord in England end a tenancy with a no-fault section 21 notice?",["Yes, with 2 months' notice","No, no-fault section 21 notices ended","Only in the first 12 months"],1,"The Renters' Rights Act ended no-fault section 21 evictions in England. A landlord now needs a legal ground.",RR,True,"Renters' Rights Act changes from 1 May 2026"),
q("rent-002","renting",1,"New tenancies in England now usually have…",["A rolling tenancy with no fixed end date","A fixed 12-month term","A fixed 6-month term"],0,"New tenancies are rolling (periodic) with no fixed end date.",RR,True,"Periodic tenancy rule"),
q("rent-003","renting",1,"To leave a rolling tenancy, how much written notice does a tenant give?",["1 month","2 months","4 months"],1,"A tenant can leave by giving 2 months' written notice, on the rent day or the day before.",RR,True,"Tenant notice period"),
q("rent-004","renting",2,"A landlord who wants you out of your home now needs…",["A legal ground and usually 4 months' notice","Nothing but a written notice","Your agreement"],0,"A landlord needs a legal ground and usually gives 4 months' notice, though some grounds allow less.",RR,True,"Landlord possession grounds"),
q("rent-005","renting",2,"How often can a landlord raise the rent in a rolling tenancy?",["Once a year, and not in the first 12 months","Whenever they give notice","Every 6 months"],0,"Rent can go up once a year, and not in the first 12 months.",RR,True,"Rent increase rule"),
q("rent-006","renting",2,"What must a landlord use to propose a rent increase?",["A text message","The official Form 4A with at least 2 months' notice","A phone call"],1,"They must use the official form (Form 4A) and give at least 2 months' notice. You can challenge an increase above market rent.",RR,True,"Form 4A and notice period"),
q("rent-007","renting",1,"A property is advertised at £1,200 a month. Can the landlord accept a bid of £1,300?",["Yes, if it is the highest bid","No, they cannot accept offers above the advertised rent","Yes, if it is paid up front"],1,"Adverts must state a specific price, and landlords cannot accept or encourage offers above it.",RR,True,"Advertised rent rule"),
q("rent-008","renting",2,"After the tenancy agreement is signed, a landlord can ask for at most how much rent in advance?",["1 month","3 months","6 months"],0,"Landlords cannot ask for rent before signing. After signing, they can ask for at most 1 month's rent in advance.",RR,True,"Rent in advance limit"),
q("rent-009","renting",1,"Can a landlord refuse to rent to you because you receive benefits or have children?",["Yes, if they prefer","No, they cannot","Yes, but only for children"],1,"Landlords cannot refuse to rent to you because you receive benefits or have children.",RR,True,"Anti-discrimination rule"),
q("rent-010","renting",3,"A Rent Repayment Order can require a landlord to repay up to how much rent?",["1 month's","6 months'","2 years'"],2,"For some offences, such as letting a property that should be licensed, tenants can apply for an order requiring repayment of up to 2 years' rent.",RR,True,"Rent Repayment Order limit"),
q("rent-011","renting",2,"In England, a tenancy deposit is capped at how many weeks' rent (for annual rent under £50,000)?",["4 weeks","5 weeks","8 weeks"],1,"The cap is 5 weeks' rent, or 6 weeks if the annual rent is £50,000 or more.",RD,True,"Deposit cap"),
q("rent-012","renting",2,"A holding deposit is capped at…",["1 week's rent","2 weeks' rent","1 month's rent"],0,"A holding deposit is capped at 1 week's rent, and only one can be taken for a property at a time.",RD,True,"Holding deposit cap"),
q("rent-013","renting",2,"Within how many days must a landlord protect a tenancy deposit in an approved scheme?",["7 days","30 days","90 days"],1,"The deposit must be protected in a government-approved scheme within 30 days of receiving it.",RD,True,"Deposit protection deadline"),
q("rent-014","renting",3,"If the tenancy goes ahead, the holding deposit must usually be returned within…",["7 days","30 days","3 months"],0,"The holding deposit must usually be returned within 7 days, whether the tenancy goes ahead or the landlord decides not to proceed.",RD,True,"Holding deposit return time"),
q("rent-015","renting",2,"A landlord can only charge a late-rent fee once rent is at least how overdue?",["1 day","7 days","14 days"],2,"A late-rent fee is only allowed once rent is at least 14 days overdue, and it is capped.",RD,True,"Late fee rule"),
q("rent-016","renting",1,"An agent asks you to pay a £150 reference check fee. Is that allowed in England?",["Yes, it is a normal charge","No, reference check fees are banned","Yes, but only once"],1,"Reference check fees and other charges for granting a tenancy are banned.",RD,True,"Banned fees"),
q("rent-017","renting",3,"Councils can fine landlords up to how much for a first breach of the fee rules?",["£500","£5,000","£50,000"],1,"Councils can fine up to £5,000 for a first breach, and up to £30,000 for a repeat breach within 5 years.",RD,True,"Fine limits"),
q("rent-018","renting",1,"What is the best way to pay a deposit so you can prove it later?",["Cash in hand","Bank transfer, keeping the receipt","Through a friend"],1,"Pay by a method you can prove, such as bank transfer, and keep receipts.",RD),
q("rent-019","renting",1,"You cannot pay rent this month. What should you do first?",["Wait until they chase you","Tell your landlord or agent as early as you can","Ignore the letters"],1,"Tell them early, ask what can be agreed in writing, and get free help from Shelter, Citizens Advice or MoneyHelper.",RP),
q("rent-020","renting",2,"You set up a standing order for your rent. Who sets it up?",["The landlord","You, with your bank","The council"],1,"A standing order is set up by you with your bank. A Direct Debit is set up by the landlord, who collects the payment.",RP),
q("rent-021","renting",1,"Does paying rent normally appear on your credit file?",["Yes, always","Normally no","Only if you pay late"],1,"Normally, paying rent does not appear on your credit file. Rent reporting services aim to change that.",RC),
q("rent-022","renting",2,"If a rent reporting service reports your payments, must lenders use that data?",["Yes, all lenders","No, many do not","Only banks do"],1,"Lenders do not have to use rent data, and many do not, so a score change is not guaranteed.",RC),
q("rent-023","renting",2,"What does Open Banking let a rent reporting service do?",["Move your money","See your rent payments with read-only access","Change your landlord's details"],1,"The service asks for read-only access to your bank transactions, finds your rent payments and reports them.",RC),
q("rent-024","renting",2,"A service gives 1 point per £1 of rent, and 100 points = £1. About what do you get back on £1,000 rent?",["£1","£10","£100"],1,"1,000 points at 100 points per £1 is £10, about 1%. Always check the current rate and fees.",RW,True,"Reward rate example is illustrative"),
q("rent-025","renting",2,"A rent-by-card service charges 1.99%. On £1,000 of rent, what is the fee?",["£1.99","£19.90","£199"],1,"1.99% of £1,000 is £19.90. Card rewards must beat that for it to make sense.",RK),
q("rent-026","renting",1,"You pay rent by credit card and do not clear the balance. What is the risk?",["Interest can cost more than the rewards","Your landlord is charged","Nothing"],0,"If you do not clear the card in full by the due date, interest can cost more than any rewards.",RK),
q("rent-027","renting",3,"Why check that rewards are worth it before changing how you pay rent?",["Rewards are often small and terms change","Rewards are always large","Landlords require it"],0,"The rewards are usually small and terms change often, so work out the real value first.",RW),
]
tax=[
q("tax-020","tax",1,"What is the standard Personal Allowance for 2026/27?",["£10,000","£12,570","£15,000"],1,"The Personal Allowance is £12,570 of income tax-free, reduced by £1 for every £2 earned over £100,000.","pb-tax-allowances",True,"Personal Allowance figure","2027-04-06"),
q("tax-021","tax",2,"A basic-rate taxpayer can earn how much savings interest tax-free under the Personal Savings Allowance?",["£500","£1,000","£5,000"],1,"Basic-rate taxpayers get £1,000, higher-rate £500 and additional-rate £0.","pb-tax-allowances",True,"Personal Savings Allowance","2027-04-06"),
q("tax-022","tax",1,"The UK tax year runs from…",["1 January to 31 December","6 April to 5 April","1 April to 31 March"],1,"The UK tax year runs from 6 April to 5 April. Allowances reset each year.","pb-tax-allowances"),
q("tax-023","tax",2,"You start a new job and get an emergency tax code. What can happen?",["You may pay too much tax for a while","You pay no tax","HMRC fines you"],0,"A new job can mean an emergency code and too much tax for a while. HMRC refunds any overpayment once corrected.","pb-tax-allowances"),
q("tax-024","tax",2,"How much gross side income can you earn without telling HMRC under the trading allowance?",["£500","£1,000","£5,000"],1,"The trading allowance is £1,000 of gross side income a year.","pb-tax-side-income",True,"Trading allowance","2027-04-06"),
q("tax-025","tax",2,"By what date is the online Self Assessment return deadline?",["31 October after the tax year","31 January after the tax year","5 April"],1,"The online Self Assessment deadline is 31 January after the tax year ends.","pb-tax-side-income",True,"Self Assessment deadline","2027-04-06"),
q("tax-026","tax",2,"You miss the Self Assessment deadline but owe no tax. Is there a penalty?",["No","Yes, an automatic £100 penalty","Only if tax is due"],1,"A late return means an automatic £100 penalty, even if no tax is owed.","pb-tax-side-income",True,"Late filing penalty","2027-04-06"),
q("tax-027","tax",3,"A marketplace shares your details with HMRC. Does that mean you owe tax?",["Yes, automatically","No, it depends on whether you are trading","Yes, 20%"],1,"Being reported doesn't automatically mean you owe tax. It depends on whether you're trading.","pb-tax-side-income"),
q("tax-028","tax",2,"Marriage Allowance lets you transfer how much of your Personal Allowance?",["£630","£1,260","£5,000"],1,"You can transfer £1,260, saving up to £252 a year, and it can be backdated up to 4 years.","pb-tax-marriage-allowance",True,"Marriage Allowance figures","2027-04-06"),
q("tax-029","tax",1,"What is the best way to claim Marriage Allowance?",["Pay a company a fee","Apply free on gov.uk","You cannot claim it"],1,"Apply for free on gov.uk. Some firms charge a cut of your refund for something you can do in minutes.","pb-tax-marriage-allowance"),
]
pen=[
q("pen-020","pensions",1,"The minimum total workplace pension contribution is 8% of qualifying earnings. What is the minimum from the employer?",["1%","3%","8%"],1,"The minimum total is 8%, with at least 3% from the employer.","pb-pen-workplace",True,"Auto-enrolment minimums","2027-04-06"),
q("pen-021","pensions",1,"What do you lose if you opt out of a workplace pension?",["Nothing","Your employer's contributions","Your State Pension"],1,"Opting out means losing your employer's contributions.","pb-pen-workplace"),
q("pen-022","pensions",1,"You get a cold call offering a 'free pension review'. What should you do?",["Give your details","Hang up, it is likely a scam","Ask for a quote"],1,"Free pension review cold calls are illegal in the UK and a classic scam opener.","pb-pen-workplace"),
q("pen-023","pensions",2,"Before moving an old pension, what should you check?",["Exit fees and valuable guarantees","Nothing, always move","Only the logo"],0,"Check for exit fees or valuable guarantees before moving anything.","pb-pen-workplace"),
q("pen-024","pensions",2,"What is the normal minimum pension age, rising from 6 April 2028?",["From 55 to 57","From 60 to 62","From 50 to 55"],0,"The normal minimum pension age is 55, rising to 57 from 6 April 2028.","pb-pen-tax-relief",True,"Normal minimum pension age","2027-04-06"),
q("pen-025","pensions",2,"Usually up to what share of a pension can be taken tax-free?",["10%","25%","50%"],1,"Usually up to 25% can be taken tax-free, capped by the lump sum allowance.","pb-pen-tax-relief",True,"Tax-free lump sum","2027-04-06"),
q("pen-026","pensions",1,"Someone offers to unlock your pension before the minimum age. What does that usually mean?",["A good deal","Huge tax charges, or stolen money","A government scheme"],1,"Offers to unlock your pension early usually mean huge tax charges, or that the money is stolen.","pb-pen-tax-relief"),
q("pen-027","pensions",2,"How many qualifying National Insurance years usually give the full new State Pension?",["10","25","35"],2,"You usually need 10 years to get any new State Pension, and 35 for the full amount.","pb-pen-state",True,"NI years for State Pension","2027-04-06"),
q("pen-028","pensions",1,"Which free service helps you find old pensions?",["The Pension Tracing Service","A cold caller","Social media"],0,"Use the government's free Pension Tracing Service to find old workplace or personal pensions.","pb-pen-state"),
]
bills=[
q("bill-020","bills",2,"Ofgem's energy price cap limits…",["Your total bill","The unit rates and standing charges","Only standing charges"],1,"The cap limits unit rates and standing charges, not your total bill. Use more and you pay more.","pb-bills-energy"),
q("bill-021","bills",1,"Does switching energy supplier interrupt your supply?",["Yes, for a few days","No, it is the same pipes and wires","Only for gas"],1,"Switching supplier doesn't interrupt your supply.","pb-bills-energy"),
q("bill-022","bills",2,"Since 17 January 2025, price rises in new broadband and mobile contracts must be…",["Hidden in the terms","Shown in pounds and pence upfront","Announced after signing"],1,"Price rises in new contracts must be shown in pounds and pence upfront.","pb-bills-broadband-mobile",True,"Ofcom pricing rule","2027-04-06"),
q("bill-023","bills",2,"A £600 phone plus £12 a month SIM-only for 24 months costs how much in total?",["£888","£1,080","£1,440"],0,"£600 + (12 x £24) = £888, versus a £45 a month contract at £1,080.","pb-bills-broadband-mobile"),
q("bill-024","bills",1,"You live alone as the only adult. What is the usual council tax discount?",["10%","25%","50%"],1,"Living alone usually gets 25% off council tax.","pb-bills-council-tax",True,"Single person discount","2027-04-06"),
q("bill-025","bills",2,"You think your council tax band is too high. Who can you check with in England and Wales?",["The Valuation Office Agency","The energy supplier","Citizens Advice only"],0,"You can check with the Valuation Office Agency, but bands can go up as well as down.","pb-bills-council-tax"),
q("bill-026","bills",2,"When is a water meter most likely to save money?",["More people than bedrooms","Fewer people than bedrooms","Large gardens only"],1,"A meter often saves money if fewer people live in your home than there are bedrooms.","pb-bills-council-tax"),
q("bill-027","bills",2,"Since January 2022, can insurers charge renewing customers more than new customers for the same policy?",["Yes","No, for home and car insurance","Only for car"],1,"Home and car insurers can't charge renewing customers more than a new customer for the same policy.","pb-bills-insurance",True,"FCA pricing rule","2027-04-06"),
q("bill-028","bills",2,"Why is paying insurance monthly often dearer?",["It includes interest","It is always free","There are no fees"],0,"Monthly payments often include interest, so pay annually if you can.","pb-bills-insurance"),
]
cb=[
q("cash-020","cashback",1,"Your cashback shows as 'pending'. What does that mean?",["It is paid","It is waiting to be confirmed","It is declined"],1,"Cashback can take weeks or months to confirm and can be declined. Don't count it until it's paid.","pb-cb-sites"),
q("cash-021","cashback",1,"Should you buy something just for the cashback?",["Yes, always","No, use it on planned purchases","Only if over 5%"],1,"Never buy something just for the cashback. Use it to make planned purchases cheaper.","pb-cb-sites"),
q("cash-022","cashback",2,"Which of these can stop cashback tracking?",["Pausing ad blockers","Using an ad blocker or coupon extension","Using the cashback app"],1,"Pause ad blockers and coupon or price extensions, and complete the purchase in the same session.","pb-cb-tracking"),
q("cash-023","cashback",2,"Which is better: a 10% voucher on £120 now, or 8% cashback later?",["The voucher, £12 now","The cashback, £9.60","They are equal"],0,"A 10% voucher saves £12 now, while 8% cashback is £9.60 later. Take the bigger, more certain saving.","pb-cb-tracking"),
q("cash-024","cashback",2,"Why might cashback be declined?",["You cancelled or returned the order","You paid on time","You used the app"],0,"Returning or cancelling the order is a common reason, as are unlisted voucher codes and excluded products.","pb-cb-tracking"),
q("cash-025","cashback",1,"Someone asks you to pay a bill in gift cards. What is it?",["A normal request","A scam","A discount"],1,"Anyone who asks you to pay a bill, fine or tax in gift cards is a scammer.","pb-cb-giftcards"),
q("cash-026","cashback",2,"What is one risk of holding unused gift card balances?",["They can be lost if the retailer goes into administration","They always double","They never expire"],0,"Unused balances can be lost if a retailer goes into administration, and some cards expire.","pb-cb-giftcards"),
]
DROP={"pen-020","pen-023","pen-025","pen-026","pen-028","bill-020","bill-021","bill-026","tax-020","tax-021","tax-022","tax-023","tax-024","tax-025","tax-026","tax-027","cash-020","cash-021","cash-022","cash-024"}  # overlap existing questions
ren,tax,pen,bills,cb=[[x for x in L if x["id"] not in DROP] for L in (ren,tax,pen,bills,cb)]
new={"renting":ren,"tax":tax,"pensions":pen,"bills":bills,"cashback":cb}
base=os.path.join(os.path.dirname(__file__),"..","data","questions")
n=0
for topic,items in new.items():
    p=os.path.join(base,topic+".json")
    d=json.load(open(p)) if os.path.exists(p) else {"topic":topic,"questions":[]}
    have={x["id"] for x in d["questions"]}
    for it in items:
        if it["id"] not in have:d["questions"].append(it);n+=1
    open(p,"w").write(json.dumps(d))
print("added",n)
