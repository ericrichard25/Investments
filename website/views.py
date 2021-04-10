from django.shortcuts import render, HttpResponse, redirect
from . models import *
from django.contrib import messages
import bcrypt

# for reduce() function to upload and preserve line spacing <br>
import functools

# for number formatting
import locale
locale.setlocale(locale.LC_ALL, 'en_US')

# for importing csv
import csv, io
from io import StringIO
from django.shortcuts import render
from django.contrib import messages

# for converting yfinance timestamp of earningsDate to string
from datetime import datetime, date

# permissions array to pass to summarizer.html and user.html
permissions = ["administrator", "analyst", "maintainer", "viewer"]

# priorities array to pass to summarizer.html and symbol.html . . . *** keep in numerical order so that array index number matches priority
priorities = [0, 1, 2, 3]

# decisions array to pass to summarizer.html and symbol.html
decisions = ["pass", "buy 1%", "buy 1.5%","buy 2%","buy 2.5%","buy 3%","buy 3.5%","buy 4%","buy 4.5%","buy 5%","buy 5.5%","buy 6%", "sell 0.5%", "sell 1%", "sell 1.5%" ]

def add_stock(request):
    if request.POST['symbol'] == "":
        messages.error(request, "No symbol entered")
        return redirect("/summarizer")

    if (',' in request.POST['symbol']):
        messages.error(request, "Separate symbols with a space (no commas).") 
        return redirect("/summarizer")
    else:
        added = []
        duplicates = []
        new_symbols = (request.POST['symbol']).split()
        for new_stock in new_symbols:
            new_stock = new_stock.upper()
            exists = Stock.objects.filter(symbol=new_stock)  
            if len(exists) > 0:
                duplicates.append(new_stock)
            else:
                Stock.objects.create(
                    symbol=new_stock,
                    summary=f"{ new_stock } THESIS: Cash , burn.\n\nCATALYSTS:\n\nVALUATION:\n\n2021 EPS avg\nprice\nfwdPE\n\nLIQUIDITY (as of 3/31/21):\ncurrent debt M\nlong-term debt M\n\nSEASONALITY:\n\nSUMMARY:\n\nEVENTS:\n\nPIPELINE:\n\nGLOSSARY:\n\nSOURCES:\n1."
                )
                added.append(new_stock)

        if (len(duplicates) > 0):
            messages.error(request, f"Duplicate symbol(s): { duplicates }")
        if (len(added) > 0):
            messages.error(request, f"Successfully added symbol(s): { added }")
        
        return redirect("/summarizer")
# end add_stock

def add_user(request):
    if(not User.objects.isAdmin(request.session['id'])):
        messages.error(request, "Permission denied")
    else:
        errors = User.objects.add_validator(request.POST)
        if len(errors) > 0:
            for key, value in errors.items():
                messages.error(request, value)
            return redirect("/summarizer")
        else:
            pw_hash = bcrypt.hashpw(request.POST['password'].encode(), bcrypt.gensalt()).decode()
            new_user = User.objects.create(
                first_name = request.POST['first_name'],
                last_name = request.POST['last_name'],
                email = request.POST['email'],
                phone = request.POST['phone'],
                password = pw_hash,
                permission = request.POST['permission'],
            )
    return redirect("/summarizer")
# end add_user

def analyster_update(request, id):
    if(not User.objects.isAssigned(request.session['id'], id)):
        messages.error(request, "Permission denied")
    else:
        # only allow assignment fields to be saved if an assignment exists for that symbol
        if (Assignment.objects.filter(symbol_id=id).exists()):
            assignment = Assignment.objects.get(symbol_id=id)
            
            if (request.POST['date_presented'] == ""):
                assignment.date_presented = assignment.date_presented
            else:
                assignment.date_presented = request.POST['date_presented']

            if (assignment.decision == request.POST['decision'] == ""):
                assignment.decision = assignment.decision
            else:
                assignment.decision = request.POST['decision']   
            
            if (request.POST['notes'] == ""):
                assignment.notes = assignment.notes
            else:
                assignment.notes = request.POST['notes']
            
            assignment.save()

            archiver = User.objects.get(id=request.session['id'])
            # create Archive record of saved fields
            Archive.objects.create(
                date_assigned = assignment.date_assigned,
                date_presented = assignment.date_presented,
                decision = assignment.decision,
                notes = assignment.notes,
                analyst_id = assignment.analyst_id,
                previous_analyst_id = assignment.previous_analyst_id,
                symbol_id = assignment.symbol_id,
                archiver_id = archiver.id,
            )
        
            messages.error(request, f"{ assignment.analyst.first_name } { assignment.analyst.last_name }'s updates for { assignment.symbol.symbol } have been saved and archived by { archiver.first_name } { archiver.last_name }.")
        
        else:
            stock = Stock.objects.get(id=id)
            messages.error(request, f"{ stock.symbol } is not assigned. Assignment must be made before fields can be saved (analyst 'Temp Temp' can be used for temporary assignment).")
    return redirect("/summarizer")
# end analyster_update

# can possible remove "archive" view since saving (analyster_update) automatically creates an archive of the update
def archive(request, id):
    if(not User.objects.isAdmin(request.session['id'])):
        messages.error(request, "Permission denied")
    else:
        stock = Stock.objects.get(id=id)
        analyst = User.objects.get(id=stock.analyst_id)
        date_assigned = stock.date_assigned

        if (request.POST['date_presented'] == ""):
            messages.error(request, "Date presented is required")
            return redirect("/summarizer")
        else:
            date_presented = request.POST['date_presented']

        decision = request.POST['decision']
        notes = request.POST['notes']
        Archive.objects.create(
            symbol=stock,
            analyst=analyst,
            date_assigned=date_assigned,
            date_presented=date_presented,
            decision=decision,
            notes=notes,
        )
    return redirect("/summarizer")
# end archive

def batch_assign(request):
    if(not User.objects.isAdmin(request.session['id'])):
        messages.error(request, "Permission denied")
        return redirect("/summarizer")
    else:
        from_analyst = User.objects.get(id=request.POST['from'])
        assignments = Assignment.objects.filter(analyst_id=from_analyst)
        to_analyst = User.objects.get(id=request.POST['to'])
        for assignment in assignments:
            assignment.analyst_id = to_analyst
            assignment.previous_analyst_id = from_analyst
            assignment.save()
    messages.error(request, f"All of { from_analyst.first_name }'s stocks have been assigned to { to_analyst.first_name }")
    return redirect("/summarizer")
#end batch_assign

def batch_delete(request):
    if(not User.objects.isAdmin(request.session['id'])):
        messages.error(request, "Permission denied")
        return redirect("/summarizer")
    else:
        stocks = Stock.objects.all()
        stocks.delete()
        assignments = Assignment.objects.all()
        assignments.delete()
    return redirect("/loader")
# end batch_delete

def comment(request, symbol):
    stock = Stock.objects.get(symbol=symbol)
    if(not User.objects.isAssigned(request.session['id'], stock.id)):
        messages.error(request, "Permission denied")
    else:
        user = User.objects.get(id=request.session['id'])
        stock = Stock.objects.get(symbol=symbol)
        new_comment = Comment.objects.create(
            analyst_id = user.id,
            symbol_id = stock.id,
            comment = request.POST['comment'],
            decision = request.POST['decision']
        )
        messages.error(request, f"New comment successfully created for { new_comment.symbol.symbol }")
    return redirect(f"/summarizer/{ symbol }")
# end comment

def contact(request):
    return render(request, "website/contact.html")
# end contact

def delete_stock(request, id):
    if(not User.objects.isAdmin(request.session['id'])):
        messages.error(request, "Permission denied")
    else:
        stock = Stock.objects.get(id=id)
        # if assignment exists then delete it
        if (Assignment.objects.filter(symbol_id=stock.id).exists()):
            assignment = Assignment.objects.get(symbol_id=stock.id)
            assignment.delete()
        stock.delete()
    return redirect("/summarizer")
# end delete_stock

def delete_user(request, id):
    if(not User.objects.isAdmin(request.session['id'])):
        messages.error(request, "Permission denied")
        return redirect(f"/user/{ id }")
    else:
        if id == request.session['id']:
            messages.error(request, "Logged in user cannot delete their own account")
            return redirect(f"/user/{ id }")
        else:
            deleted_user = ""
            user = User.objects.get(id=id)
            deleted_user = user.first_name + user.last_name
            user.delete()
            messages.error(request, f"User { deleted_user } has been deleted")
            return redirect("/summarizer")
# end delete_user

def go_to(request):
    errors = {}
    try:
        stock = request.POST['symbol'].upper()
        symbol = Stock.objects.get(symbol=stock)
        return redirect(f"/summarizer/{ symbol.symbol }")
    except:
        errors['exists'] = "No matching symbol found."
        return redirect("/summarizer")
# end go_to

def index(request):
    if 'id' in request.session:
        return redirect("/summarizer")
    return render(request, "website/index.html")
# end index

def individual_assign(request):
    if(not User.objects.isAdmin(request.session['id'])):
        messages.error(request, "Permission denied")
    else:
        new_assignments = []
        post_to_analyst_id = int(request.POST['to_analyst'])
        post_assign_stocks = request.POST.getlist('checked_stocks')
        for stock in post_assign_stocks:
            stock = Stock.objects.get(id=stock)
            # if the assignment already exists then update with new analyst
            if (Assignment.objects.filter(symbol_id=stock.id).exists()):
                exists = Assignment.objects.get(symbol_id=stock.id)
                exists.previous_analyst_id = exists.analyst_id
                exists.analyst_id = post_to_analyst_id
                exists.date_assigned = datetime.today().date()
                exists.save()
                new_assignments.append(stock.symbol)
            # if the assignment doesn't exist then create new assignment
            else:
                exists = Assignment.objects.create(
                    symbol_id=stock.id,
                    analyst_id=post_to_analyst_id,
                    date_assigned = datetime.today().date(),
                )
                new_assignments.append(exists.symbol.symbol)
        messages.error(request, f"{ exists.analyst } has been assigned the following stock(s): { new_assignments }")
    return redirect("/summarizer")
# end individual_assign

def internships(request):
    return render(request, "website/internships.html")
# end internships

def investing_philosophy(request):
    return render(request, "website/investing_philosophy.html")
# end investing_philosophy

def loader(request):
    context = {
        "stocks": Stock.objects.all(),
    }
    return render(request, "website/loader.html", context)
# end loader

def login(request):
    errors = User.objects.login_validator(request.POST)
    if len(errors) > 0:
        for key, value in errors.items():
            messages.error(request, value)
        return redirect("/login_page")
    else:   
        user = User.objects.filter(email=request.POST['email'])
        if user:
            logged_user = user[0]
            if bcrypt.checkpw(request.POST['password'].encode(), logged_user.password.encode()):
                request.session['id'] = logged_user.id
                request.session['permission'] = logged_user.permission
                request.session['first_name'] = logged_user.first_name
                return redirect("/summarizer")
        else:
            messages.error(request, "Incorrect login")
    return redirect("/")
# end login

def login_page(request):
    return render(request, "website/login.html")
# end login_page

def logout(request):
    request.session.clear()
    return redirect("/login_page")
# end logout

def nav(request):
    if(not User.objects.isAdmin(request.session['id'])):
        messages.error(request, "Permission denied")
        return redirect("/summarizer")
    else:
        try:
            new_nav = float(request.POST['nav'])
            # check if NAV entry exists and create entry if it doesn't
            exists = NAV.objects.all()
            if (len(exists) > 0):
                exists[0].nav = new_nav
                exists[0].save()
            else:
                NAV.objects.create(nav=new_nav)
            
            # update target positions of all stocks
            Stock.objects.updateTargetPositions()
            messages.error(request, "Successfully saved new NAV and updated all target positions")
            return redirect("/summarizer")
        except ValueError:
            messages.error(request, "Unable to save new NAV")
            return redirect("/summarizer")
# end nav

def performance(request):
    context = {
        "top_ideas": Top_Idea.objects.all()
    }
    return render(request, "website/performance.html", context)
# end performance

# start quintile_weights
def quintile_weights(request):
    if(not User.objects.isAdmin(request.session['id'])):
        messages.error(request, "Permission denied")
    else:
        quintiles = Quintile.objects.all()
        for quintile in quintiles:
            if (request.POST[f"{ quintile.quintile }"] == ""):
                new_weight = quintile.weight
            else:
                new_weight = float(request.POST[f"{ quintile.quintile }"])
            quintile.weight = new_weight
            quintile.save()
        
        # update target positions of all stocks
        Stock.objects.updateTargetPositions()
        messages.error(request, "Successfully saved new quintile weight(s) and updated all target positions")
    return redirect("/summarizer")
# end quintile_weights

def set_priority(request):
    if(not User.objects.isAdmin(request.session['id'])):
        messages.error(request, "Permission denied")
    else:
        assign_stocks = request.POST.getlist('checked_stocks')
        success_array = []
        error_array = []
        for stock in assign_stocks:
            stock = Stock.objects.get(id=stock)
            if (Assignment.objects.filter(symbol_id=stock.id).exists()):
                assignment = Assignment.objects.get(symbol_id=stock.id)
                assignment.priority = int(request.POST['priority'])
                assignment.save()
                success_array.append(stock.symbol)
            else:
                error_array.append(stock.symbol) 
        if (len(success_array) > 0):
            messages.error(request, f"Priority successfully set for: { success_array }.")
        if (len(error_array) > 0):
            messages.error(request, f"Stock(s) requiring an assignment before a priority can be set: { error_array }")
    return redirect("/summarizer")
# end set_priority

# testing for line breaks upload (may not need this)
def splitkeepsep(s, sep):
    return functools.reduce(lambda acc, elem: acc[:-1] + [acc[-1] + elem] if elem == sep else acc + [elem], re.split("(%s)" % re.escape(sep), s), [])
# end splitkeepsep

def summarizer(request):
    if 'id' not in request.session:
        messages.error(request, "Please log in")
        logged_in = False
        return redirect("/login_page")
    else:
        user = User.objects.get(id=request.session['id'])
        logged_in = True

        # update target positions each time page reloads
        Stock.objects.updateTargetPositions()

    # get NAV and format with commas
        exists = NAV.objects.all()
        if (len(exists) > 0):
            nav = exists[0].nav
        else:
            nav = 0
        
        nav = locale.format(f"%d", nav, grouping=True)

    context = {
            "analysts": User.objects.filter(permission="analyst"),
            "decisions": decisions,
            "logged_in": logged_in,
            "nav": nav,
            "permissions": permissions,
            "priorities": priorities,
            "priority_count": Assignment.objects.countPriorities(priorities),
            "quintiles": Quintile.objects.all(),
            "session_id": request.session['id'],
            "stocks": Stock.objects.all(),
            "user": user,
            "users": User.objects.all().annotate(assigned_stocks=models.Count('assignments')),
            # events = Event.objects.all().annotate(participants=models.Count('participant'))

    }
    return render(request, "website/summarizer.html", context)
# end summarizer

def symbol(request, symbol=""):
    # logged in user info must still be passed in context dictionary to symbol.html template even though header code exists on summarizer.html template
    user = User.objects.get(id=request.session['id'])
    
    stock = Stock.objects.get(symbol=symbol)
    comments = Comment.objects.filter(symbol=stock)
    archives = Archive.objects.filter(symbol=stock)
    # the yfinance scraper does not return consensus PT
    # all uses of "data" commented out for now because API loads very slowly
    # data = Stock.objects.yfinance(symbol)
    
    # format market cap 
    # market_cap = round(data['marketCap'] / 1000000)

    # # format mostRecentQuarter timestamp to string (yfinance does not return "earningsDate" like yahoo Rapid API does)
    # earnings_date = datetime.fromtimestamp(data['mostRecentQuarter'])

    analysts = User.objects.filter(permission="analyst")
    quintiles = Quintile.objects.all()
    context = {
        "user": user,
        "archives": archives,
        "comments": comments,
        "decisions": decisions,
        "stock": stock,
        "analysts": analysts,
        "quintiles": quintiles,
        # commented out because API loads very slowly
        # "data": data,
        # "market_cap": market_cap,
        # "earnings_date": earnings_date,
        "priorities": priorities
    }
    return render(request, "website/symbol.html", context)
# end symbol

def update_stock(request, symbol): 
    if(not User.objects.isAdmin(request.session['id'])):
        messages.error(request, "Permission denied")
    else:  
        errors = {}
        stock = Stock.objects.get(symbol=symbol)
        if (Assignment.objects.filter(symbol_id=stock.id).exists()):
            assignment_exists = Assignment.objects.get(symbol_id=stock.id)
        else:
            assignment_exists = False

        # format post info
        if (request.POST['first_pt'] == ""):
            post_first_pt = 0
        else:
            post_first_pt = float(request.POST['first_pt'])
        
        if (request.POST['price'] == ""):
            post_price = 0
        else:
            post_price = float(request.POST['price']) 
        
        if(request.POST['analyst_id'] == ""):
            post_analyst_id = False
        else:
            post_analyst_id = int(request.POST['analyst_id'])
        
        if (request.POST['quintile_id'] == ""):
            print("****")
            print(request.POST['quintile_id'])
            post_quintile_id = False   
        else:
            post_quintile_id = int(request.POST['quintile_id'])  
        
        if (request.POST['consensus_pt'] == ""):
            post_consensus_pt = 0
        else: 
            post_consensus_pt = float(request.POST['consensus_pt']) 
        
        if (request.POST['buy_price'] == ""):
            post_buy_price = 0    
        else:
            post_buy_price = float(request.POST['buy_price'])
        
        if (request.POST['priority'] == ""):
            post_priority = False
        elif (assignment_exists):
            try:
                post_priority = int(request.POST['priority'])
                assignment_exists.priority = post_priority
            except ValueError:
                post_priority = False
        else:
            post_priority = False
            messages.error(request, "Stock assignment required before a priority can be set")

        post_summary = request.POST['summary']
        # end format post info
        
        # first_pt validation
        try:
            stock.first_pt = post_first_pt
            if (post_first_pt >= 0):
                stock.first_pt = post_first_pt
                first_upside = (post_first_pt / post_price - 1) * 100
                stock.first_upside = first_upside 
            else:
                stock.first_pt = 0
                errors['first_pt'] = "Invalid First PT. Enter value as a positive integer or decimal with no commas (or zero). Default of $0.00 has been saved."
        except ValueError:
            stock.first_pt = 0
            errors['first_pt'] = "Invalid First PT. Enter value as a positive integer or decimal with no commas (or zero). Default of $0.00 has been saved."
        # end first_pt validation

        # update analyst and previous analyst or create new assignment
        if (assignment_exists):
            assignment_exists.previous_analyst_id = assignment_exists.analyst_id
            assignment_exists.analyst_id = User.objects.get(id=post_analyst_id)
            assignment_exists.save()
        elif (post_analyst_id):
            Assignment.objects.create(
                symbol_id = stock.id,
                analyst_id = post_analyst_id,
                date_assigned = datetime.today().date(),
            )
        else:
            pass

        # check if a quintile has been assigned
        try:
            if (post_quintile_id):
                quintile = Quintile.objects.get(id=post_quintile_id)
                stock.quintile_id = quintile.id
                stock.weight = quintile.weight
                stock.save()
                Stock.objects.updateTargetPositions()
                messages.error(request, "Successfully saved new quintile and updated target position")
        except ValueError:
            pass

        # consensus_pt validation
        try:
            stock.consensus_pt = post_consensus_pt
            consensus_upside = (post_consensus_pt / post_price - 1) * 100
            stock.consensus_upside = consensus_upside
        except ValueError:
            pass
        # end consensus_pt validation

        # buy_price validation
        try:
            stock.buy_price = post_buy_price
            if (post_buy_price >= 0):
                stock.buy_price = post_buy_price
            else:
                stock.buy_price = 0
                errors['buy_price'] = "Invalid Buy Price. Enter value as a positive integer or decimal with no commas (or zero). Default of $0.00 has been saved."
        except ValueError:
                stock.buy_price = 0
                errors['buy_price'] = "Invalid Buy Price. Enter value as a positive integer or decimal with no commas (or zero). Default of $0.00 has been saved."
        # end buy_price validation

        # update priority
        if (post_priority):
            stock.priority = post_priority
        # end update priority
        
        stock.summary = post_summary
        stock.save()

        if len(errors) > 0:
            for key, value in errors.items():
                messages.error(request, value)
    return redirect(f"/summarizer/{ symbol }")
# end update_stock

def update_user(request, id):
    if(not User.objects.isAdmin(request.session['id'])):
        messages.error(request, "Permission denied")
        return redirect(f"/user/{ id }")
    else:
        errors = User.objects.update_validator(request.POST)
        if len(errors) > 0:
            for key, value in errors.items():
                messages.error(request, value)
            return redirect(f"/user/{ id }")
        else:
            updated_user = User.objects.get(id=id)
            updated_user.first_name = request.POST['first_name']
            updated_user.last_name = request.POST['last_name']
            updated_user.email = request.POST['email']
            updated_user.phone = request.POST['phone']
            updated_user.permission = request.POST['permission']
            pw_hash = bcrypt.hashpw(request.POST['password'].encode(), bcrypt.gensalt()).decode()
            updated_user.password = pw_hash
            updated_user.save()
            messages.error(request, f" User { updated_user.first_name } { updated_user.last_name } has been updated")
            return redirect(f"/user/{ id }")
# end update_user

def upload(request):
    # To write the "upload" function that imports the csv file I used the article below (with a few changes).
    # https://simathapa111.medium.com/how-to-upload-a-csv-file-in-django-3a0d6295f624
    # Some things I noticed while uploading:
        # 1. In the very first row, the "first_pt" column (right after "symbol") cannot be empty. Other rows can have an empty "first_pt" but for the first row I put in "0.00"
        # 2. Having an empty "updated_at" column creates problems so I took it out of the Excel file (an empty "created_at" column is needed.)
        # 3. Not sure why it didn't like analyst_id = 18 (Bob) so I uploaded all stocks with analyst_id = 3 (Luca).
        # 4. Dates must be in YYYY-MMM-DD format and it did not like dates that are very far back (i.e. 1900-01-01) so I made all these 2021-01-01. 
    csv_file = request.FILES['file']

    # check if it is a csv file
    if not csv_file.name.endswith('.csv'):
        messages.error(request, 'Not a .csv file')

    # .decode("UTF-8") and .decode("latin-1") both work if "summary" field is clean data (quotes are ok) but if it contains commas then it incorrectly identifies where the next field starts (even with double quotes enclosing the summary)

    # *** use latin-1 instead of UTF-8 character set and collation . . . for sorting latin-1-swedish
    data_set = csv_file.read().decode('latin-1')

    # setup a stream which is when we loop through each line we are able to handle a data in a stream
    io_string = io.StringIO(data_set, newline='')

    added = []
    duplicates  =[]
    # I added the "for row in io_string" line
    # I followed steps for changing delimiter on Mac to "+" and "|" but it continues saving .csv with ","
    # https://www.techwalla.com/articles/how-to-save-an-excel-spreadsheet-as-pipe-delimited

    for row in io_string:
        for column in csv.reader(io_string, dialect=csv.excel_tab, delimiter=',', quotechar='"'):
            new_symbol = column[0].upper()
            exists = Stock.objects.filter(symbol=new_symbol)
            if (len(exists) > 0):
                if (new_symbol not in duplicates):
                    duplicates.append(new_symbol)
            else:    
                Stock.objects.create(
                    symbol=column[0].upper(),
                    first_pt=column[1],
                    consensus_pt=column[2],
                    analysis_date=column[3],
                    analysis_price=column[4],
                    summary=column[5],
                    created_at=column[6],
                    analyst_id=column[7],
                    quintile_id=column[8],
                    price=column[9],
                    last_price=column[10],
                    updated_at=column[11],
                )
                added.append(new_symbol)

    if (len(duplicates) > 0):
        messages.error(request, f"Duplicate symbol(s): { duplicates }")
    if (len(added) > 0):
        messages.error(request, f"Successfully added symbol(s): { added }")

    return redirect("/loader")
# end upload

def user(request, id):
    logged_in_id = request.session['id']
    if((not User.objects.isAdmin(logged_in_id)) and (not id == (logged_in_id))):
        messages.error(request, "Permission denied")
        return redirect("/summarizer")
    else:
        user = User.objects.get(id=id)
        archives = Archive.objects.filter(analyst_id=user.id)
        context = {
            "archives": archives,
            "permissions": permissions,
            "user": user
        }
        return render(request, "website/user.html", context)
# end user