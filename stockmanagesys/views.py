from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import Stock, Stock_History_log, Category
from .forms import *
from django.http import HttpResponse
import csv
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from django.db.models import F, Q 


@login_required
def issue_items(request, pk):
    stock_item = Stock.objects.get(id=pk)
    form = IssueForm(request.POST or None, instance=stock_item, initial={'issue_by': request.user.username})
    if form.is_valid():
        instance = form.save(commit=False)
        instance.receive_quantity = 0
        issue_quantity = instance.issue_quantity
        if issue_quantity <= 0:
            messages.warning(request, "Issue quantity must be greater than zero.")
        else:
            if instance.quantity < issue_quantity:
                messages.warning(request, "Not enough stock available. Current quantity is " + str(instance.quantity))
                return redirect(request.META.get('HTTP_REFERER', '/'))
            instance.quantity -= issue_quantity
            messages.success(request, "Issued SUCCESSFULLY. " + str(instance.quantity) + " " + str(instance.item_name) + "s now left in Store")
            instance.save()
            return redirect('stock_detail', pk=stock_item.id)

    context = {
        "title": 'Issue ' + str(stock_item.item_name),
        "form": form,
        "quantity_available": stock_item.quantity,
        "stock_item": stock_item
    }
    return render(request, "issue_item.html", context)



@login_required
def add_category(request):
    form = CategoryForm(request.POST or None)
    if form.is_valid():
        category = form.save(commit=False)
        category.name = category.name.upper()
        category.save()
        return redirect('/list_item')
    context = {
        "form": form,
        "title": "name",
    }
    return render(request, "add_category.html", context)


@login_required 
def receive_items(request, pk):
    stock_item = Stock.objects.get(id=pk)
    if request.method == 'POST':
        form = ReceiveForm(request.POST, instance=stock_item)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.issue_quantity = 0
            instance.quantity += instance.receive_quantity
            instance.receive_by = request.user.username
            instance.save()
            messages.success(request, f"Received SUCCESSFULLY. {instance.quantity} {instance.item_name}s now in Store")
            return redirect('stock_detail', pk=stock_item.id)
    else:
        form = ReceiveForm(instance=stock_item)
        form.fields['receive_by'].initial = request.user.username  # set the current user's username as the value of the hidden field

    context = {
        "title": 'Restock ' + str(stock_item.item_name),
        "stock_item": stock_item,
        "form": form,
    }
    return render(request, "receive_items.html", context)

@login_required
def delete_items(request, pk):
	queryset = Stock.objects.get(id=pk)
	if request.method == 'POST':
		queryset.delete()
		return redirect('/list_item')
	return render(request, 'delete_items.html')

@login_required
def update_items(request, pk):
    queryset = Stock.objects.get(id=pk)
    form = StockUpdateForm(request.POST or None, instance=queryset, request=request)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, 'Item updated successfully!')
            return redirect('/list_item')

    context = {
        'form': form,
        "title": 'Update Item name & Category : ' + str(queryset.item_name),
    }
    return render(request, 'add_items.html', context)


@login_required
def user_profile(request):
     pass




@login_required
def add_items(request):
    if request.method == 'POST':
        form = StockCreateForm(request.POST, user=request.user)
        if form.is_valid():
            stock = form.save(commit=False)
            stock.item_name = stock.item_name.upper()
            stock.created_by = request.user.username
            stock.save()
            messages.success(request, 'Item added successfully!')
            return redirect('/list_item')
    else:
        form = StockCreateForm(user=request.user)
    context = {
        "form": form,
        "title": "Add Item",
    }
    return render(request, "add_items.html", context)


@login_required
def stock_detail(request, pk):
	queryset = Stock.objects.get(id=pk)
	context = {
		"title": queryset.item_name,
		"queryset": queryset,
	}
	return render(request, "stock_detail.html", context)

@login_required
def list_item(request):
    title = 'Stocks'
    form = StockSearchForm(request.POST or None)
    queryset = Stock.objects.all()
   # p = Paginator(Stock_History_log.objects.all(),20)
   # page = request.GET.get('page')
    #  query = p.get_page(page)

    context = {
        "title": title,
        "queryset": queryset,
        "form": form,
      #  "query": query,
    }

    if request.method == 'POST':
        category = form['category'].value()
        sort_order = form['sort_order'].value()
        queryset = Stock.objects.filter(item_name__icontains=form['item_name'].value())
        if category != '':
            queryset = queryset.filter(category_id=category)

        if sort_order == 'ascending':
            queryset = queryset.order_by('quantity')
        elif sort_order == 'descending':
            queryset = queryset.order_by('-quantity')
        
        context = {
            "form": form,
            "title": title,
            "queryset": queryset,
        }
        if form['export_to_CSV'].value() == True:
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="Stock_List.csv"'
            writer = csv.writer(response)
            writer.writerow(['CATEGORY', 'ITEM NAME', 'QUANTITY'])
            instance = queryset
            for stock in instance:
                writer.writerow([stock.category, stock.item_name, stock.quantity])
            return response

    return render(request, "list_item.html", context)






def home(request):
	# check if logging in
	if request.method == 'POST':
		username = request.POST['username']
		password = request.POST['password']
		# authenticate
		user = authenticate(request, username=username, password=password)
		if user is not None:
			login(request, user)
			messages.success(request, 'Login Successfully!')
			return redirect('list_item')
		else:
			messages.success(request, 'Authentication Error!! Try Again!!')
			return redirect('home')
	else:		
		return render(request, 'home.html', {})

@login_required
def logout_user(request):
	logout(request)
	messages.success(request, 'You have been logged out!!')
	return redirect('home')



@login_required 
def reorder_level(request, pk):
    queryset = Stock.objects.get(id=pk)
    form = ReorderLevelForm(request.POST or None, instance=queryset, request=request)
    if form.is_valid():
        instance = form.save()
        messages.success(request, f"Reorder level for {instance.item_name} is updated to {instance.reorder_level}.")
        return redirect('/stock_detail/'+str(instance.id))

    context = {
        'instance': queryset,
        'form': form,
    }
    return render(request, 'reorder_level.html', context)

@login_required
def list_history(request):
    header = 'LIST OF ITEMS'
    form = StockHistorySearchForm(request.POST or None)
    queryset = Stock_History_log.objects.all()
    sort_order = request.GET.get('sort', '-last_updated')
    if sort_order not in ['-last_updated', 'last_updated']:
        sort_order = '-last_updated'
    queryset = queryset.order_by(sort_order)
   # p = Paginator(queryset, 14)
   # page = request.GET.get('page')
 #   query = p.get_page(page)
    context = {
        "header": header,
        "queryset": queryset,
        "form": form,
     #   "query": query,
    }
    if request.method == 'POST':
        category = form['category'].value()
        queryset = Stock_History_log.objects.filter(
                            item_name__icontains=form['item_name'].value(),
                            last_updated__range=[form['start_date'].value(),form['end_date'].value()]
                        )

        if form['export_to_CSV'].value() == True:
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="Stock History.csv"'
            writer = csv.writer(response)
            writer.writerow(
                ['CATEGORY', 
                'ITEM NAME',
                'QUANTITY', 
                'ISSUE QUANTITY', 
                'RECEIVE QUANTITY', 
                'RECEIVE BY', 
                'ISSUE BY', 
                'LAST UPDATED'])
            instance = queryset
            for stock in instance:
                writer.writerow(
                [stock.category, 
                stock.item_name, 
                stock.quantity, 
                stock.issue_quantity, 
                stock.receive_quantity, 
                stock.receive_by, 
                stock.issue_by, 
                stock.last_updated])
            return response

        context = {
        "form": form,
        "header": header,
        "queryset": queryset,
        
        }
    return render(request, "list_history.html",context)
