"""Batch 4: questions for the guides that had the fewest (<=3). Each is written from the guide named in learn_more.
Run: python3 scripts/new_questions_batch4.py && python3 scripts/sync_qbank.py"""
import json,os,random,re,difflib
base=os.path.join(os.path.dirname(__file__),"..","data","questions")
R="2027-05-01"
def Q(topic,d,question,options,answer,expl,learn,vol=None):
    return dict(topic=topic,d=d,question=question,options=options,answer=answer,expl=expl,learn=learn,vol=vol)
S=[
Q("banking",1,"Which payment is you 'pushing' a fixed amount on set dates?",["Direct Debit","Standing order","Card payment"],1,"A standing order is fixed and controlled by you. With a Direct Debit the company pulls the money, and the amount can vary.","pb-bank-direct-debits"),
Q("banking",1,"A Direct Debit takes the wrong amount. What must your bank do?",["Refund you straight away","Ask you to wait 30 days","Nothing"],0,"Under the Direct Debit Guarantee, your bank must refund you straight away if there is an error in the amount or date.","pb-bank-direct-debits"),
Q("banking",2,"Does a card payment count towards a bank switch's Direct Debit requirement?",["Yes","No","Only if over £10"],1,"A card payment is neither a Direct Debit nor a standing order, so it doesn't count towards switch bonus rules.","pb-bank-direct-debits"),
Q("banking",2,"For switch offers, a Direct Debit usually counts as active once it has…",["Been set up","Collected at least one payment","Run for 3 months"],1,"Usually each Direct Debit must have collected at least one payment, so set them up on the new account early.","pb-bank-direct-debits"),
Q("banking",2,"Since April 2020, how are overdrafts priced in the UK?",["Fixed daily fees","A single annual interest rate","Monthly fees only"],1,"FCA rules mean overdrafts use a single annual interest rate. Banks can't charge fixed daily or monthly overdraft fees.","pb-bank-overdrafts",R),
Q("banking",2,"£500 overdrawn all year at about 40% costs roughly…",["£20","£200","£500"],1,"40% of £500 is about £200. That is far more than most personal loans cost.","pb-bank-overdrafts"),
Q("banking",1,"What is the first step to get out of your overdraft?",["Find your real balance: balance minus the overdraft","Raise the limit","Ignore it"],0,"Work out what you really have by taking the overdraft off your balance, then lower the limit gradually.","pb-bank-overdrafts"),
Q("banking",1,"Where can you get free debt advice?",["StepChange, Citizens Advice or MoneyHelper","A company that charges a fee","A social media group"],0,"Never pay a company for debt advice. Free help is available from StepChange, Citizens Advice and MoneyHelper.","pb-bank-overdrafts"),
Q("saving",2,"A regular saver pays 6% AER. You pay in £200 a month for 12 months. You earn roughly…",["£144","£78","£12"],1,"Your average balance is only about £1,300, so you earn roughly £78, not the £144 the headline rate suggests.","pb-save-regular-savers"),
Q("saving",2,"Why is a regular saver's headline rate misleading?",["Most of your money isn't there for the whole year","Interest is taxed twice","The rate is fixed for ever"],0,"You pay in a little at a time, so your average balance is much lower than the total paid in.","pb-save-regular-savers"),
Q("saving",1,"What usually happens after a regular saver's 12-month term ends?",["The money moves to a lower rate","The rate doubles","The account is frozen"],0,"After the fixed term, the money usually moves to a lower rate.","pb-save-regular-savers"),
Q("saving",2,"In a regular saver, can you usually make up a missed month later?",["Yes, any time","No, missed months can't be made up","Only in the last month"],1,"Missed months generally can't be made up, and there is often a monthly maximum.","pb-save-regular-savers"),
Q("saving",1,"Premium Bonds enter you into a prize draw instead of paying…",["Interest","Dividends","Rent"],0,"Each £1 bond is entered into a monthly prize draw instead of earning interest.","pb-save-premium-bonds"),
Q("saving",1,"Are Premium Bond prizes taxed?",["Yes, at 20%","No, they're tax-free","Only above £500"],1,"Prizes are tax-free, which suits higher-rate taxpayers who've used their Personal Savings Allowance.","pb-save-premium-bonds"),
Q("saving",2,"The advertised Premium Bonds prize fund rate is…",["A guaranteed return","An average, so many small holders win little","What everyone earns"],1,"It is an average. Most holders with small amounts win little or nothing in many months.","pb-save-premium-bonds"),
Q("saving",2,"The maximum you can hold in Premium Bonds is…",["£5,000","£50,000","£500,000"],1,"You can hold from £25 up to £50,000, and they are 100% backed by HM Treasury.","pb-save-premium-bonds",R),
Q("saving",1,"The FSCS protects up to how much per person, per banking licence?",["£85,000","£120,000","£250,000"],1,"The limit is £120,000 per person per banking licence since 1 December 2025.","pb-save-fscs",R),
Q("saving",2,"You and a partner hold a joint account. How much does the FSCS cover?",["£120,000 in total","Up to £120,000 for each person","£60,000 each"],1,"Joint accounts are covered up to £120,000 for each person.","pb-save-fscs",R),
Q("saving",2,"Two bank brands share one banking licence. What is the FSCS limit across both?",["£120,000 each","One £120,000 limit shared","£240,000 each"],1,"Savings across brands that share a licence share one limit, so check which brands belong together.","pb-save-fscs",R),
Q("saving",2,"Which of these is not covered by the FSCS?",["Money held on a crypto exchange","A savings account at a UK-authorised bank","A building society account"],0,"Crypto, and money held on crypto exchanges, isn't covered. FSCS also doesn't cover normal investment losses from market falls.","pb-save-fscs"),
Q("investing",1,"Before taking a free share offer, what should you check first?",["The firm is on the FCA Register","The app's colour","How many ads it runs"],0,"Check the firm is authorised, plus any minimum deposit, holding period and fees after the promotion.","pb-inv-free-shares"),
Q("investing",2,"What range of value do most people get from a free share?",["The lower end","The top prize","Always the same"],0,"The possible range is wide, and most people get the lower end.","pb-inv-free-shares"),
Q("investing",1,"Should you deposit more than you're comfortable investing to unlock a bonus?",["Yes, bonuses are free money","No, the value of the share can fall","Only on Fridays"],1,"Don't deposit more than you're comfortable investing just to unlock a bonus. A free share is still an investment.","pb-inv-free-shares"),
Q("investing",1,"A crypto exchange fails. Is your money protected by the FSCS?",["Yes, up to £120,000","No","Only for the first year"],1,"There's no FSCS protection if a crypto exchange fails, and no Financial Ombudsman route for many complaints.","pb-inv-crypto-risks"),
Q("investing",2,"How fast can crypto prices fall?",["50% or more, quickly","Never more than 5%","Only slowly"],0,"Crypto can swing wildly, with falls of 50% or more happening quickly.","pb-inv-crypto-risks"),
Q("investing",1,"Who should you give your crypto wallet recovery phrase to?",["Support staff","Nobody","A friend"],1,"Never share it. Anyone with your recovery phrase owns your crypto.","pb-inv-crypto-risks"),
Q("credit",2,"Buy Now Pay Later agreements taken out from 15 July 2026 are…",["Regulated by the FCA","Not regulated","Always free"],0,"They are regulated by the FCA, lenders must check affordability, and you can complain to the Financial Ombudsman.","pb-credit-bnpl",R),
Q("credit",2,"Are BNPL agreements taken out before 15 July 2026 covered by the new rules?",["Yes","No","Only if unpaid"],1,"Agreements from before that date are not covered.","pb-credit-bnpl",R),
Q("credit",1,"A sensible BNPL rule is to only use it for things you…",["Can't afford","Could afford to pay for today","Don't need"],1,"Only use BNPL for things you could afford today, keep a list of every plan, and pay from an account that always has the money.","pb-credit-bnpl"),
Q("credit",2,"What can happen if you miss BNPL payments?",["Nothing","Late fees, a credit file impact, or debt collectors","Your balance doubles"],1,"Late fees, missed payments reported to your credit file, and debt collectors are all possible.","pb-credit-bnpl"),
Q("shopping",2,"A £50 gift card at 4% off, plus 50 loyalty points worth 50p, saves…",["£2","£2.50","£5"],1,"4% of £50 is £2, plus 50p of loyalty points makes £2.50.","pb-shop-supermarket-stacking"),
Q("shopping",1,"You buy supermarket gift cards on a credit card. What must you do?",["Clear it in full","Pay the minimum","Nothing"],0,"Clear it in full so interest doesn't wipe out the saving.","pb-shop-supermarket-stacking"),
Q("shopping",2,"Why keep gift card balances low?",["Unused balances can be lost if the retailer collapses","They expire daily","They cost interest"],0,"If a retailer collapses, unused balances can be lost, so buy only what you'll spend soon.","pb-shop-supermarket-stacking"),
Q("shopping",2,"1,000 points = £10 at the till, or £30 with a partner. The partner value is…",["The same","Three times the value","Half the value"],1,"£30 against £10 is three times the value, which is why checking partner rewards pays off.","pb-shop-loyalty"),
Q("shopping",1,"Should you buy things you don't need to earn loyalty points?",["Yes, always","No: 10% back on an unneeded purchase is still 90% spent","Only on weekends"],1,"Don't buy things you don't need just to earn points.","pb-shop-loyalty"),
]
# assign ids, shuffle options, drop near-duplicates of existing questions
pref={"banking":"bank","saving":"save","investing":"inv","credit":"cred","shopping":"shop"}
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
