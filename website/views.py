from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView
from openai import OpenAI
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Order, Message, Reviews, CustomerProfile
from .forms import OrderForm, MessageForm, CustomSignupForm
from django.contrib import messages
from django.db.models import Avg
import json

# These intent dictionaries are for selecting urls and button names depending on the intent given by user input
# variables are created and set to intent route and labels using the intent context passed from classift intent function below
# on lines 243 - 249
INTENT_ROUTE_MAP = {
    'about': '/about/',
    'contact': '/contact/',
    'orders': '/orders/',
    'reviews': '/reviews/',
    'login': '/account/login/',
    'account': '/user-account/',
    'privacy': '/privacy-policy/'
}

INTENT_CTA_LABELS = {
    'about': 'Go to About',
    'contact': 'Go to Contact',
    'orders': 'Go to Orders',
    'reviews': 'Go to Reviews',
    'login': 'Go to Login',
    'account': 'Go to Account',
    'privacy': 'Go to Privacy Policy'
}


def classify_intent_not_loggedin(message):
    text = (message or '').lower()

    intent_keywords = {
        'orders': ['order', 'quote', 'price', 'pricing', 'package', 'service cost', 'budget'],
        'contact': ['contact', 'email', 'phone', 'call', 'reach'],
        'reviews': ['review', 'rating', 'testimonial', 'feedback'],
        'about': ['about', 'who are you', 'company', 'business'],
        'login': ['login', 'logout', 'sign in', 'sign up', 'account', 'profile'],
        'privacy':['data', 'privacy', 'account details', 'profile information', 'user information', 'privacy policy'],
    }

    for intent, keywords in intent_keywords.items():
        if any(keyword in text for keyword in keywords):
            return intent, 0.9

    return 'general', 0.35

def classify_intent_loggedin(message):
    text = (message or '').lower()

    intent_keywords = {
        'orders': ['order', 'quote', 'price', 'pricing', 'package', 'service cost', 'budget'],
        'contact': ['contact', 'email', 'phone', 'call', 'reach'],
        'reviews': ['review', 'rating', 'testimonial', 'feedback'],
        'about': ['about', 'who are you', 'company', 'business'],
        'account': ['account', 'profile'],
        'privacy':['data', 'privacy', 'account details', 'profile information', 'user information', 'privacy policy'],
    }

    for intent, keywords in intent_keywords.items():
        if any(keyword in text for keyword in keywords):
            return intent, 0.9

    return 'general', 0.35

# Create your views here.
def home(request):
    reviews = Reviews.objects.all()
    if reviews.exists():
        average_rating = reviews.aggregate(avg_rating=Avg('rating'))['avg_rating']
        context = {
            'reviews': reviews,
            'overall_rating': round(average_rating, 1) if average_rating is not None else 0,
            'total_reviews': reviews.count(),
        }
        return render(request, 'home.html', context)
    return render(request, 'home.html')

def logout_confirm(request):
    return render(request, 'logout-confirm.html')

def logout_user(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect("home")

# subclassing - something I need to remember because it is very powerful
class CustomLoginView(LoginView):
    template_name = "registration/login.html"
    def form_valid(self, form):
        messages.success(self.request, "You have successfully logged in.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("user-account")

def about(request):
    return render(request, 'about.html')

def apps(request):
    return render(request, 'apps.html')

def contact(request):
    return render(request, 'contact.html')

def privacy(request):
    return render(request, 'privacy.html')

def account(request):
    order = Order.objects.filter(user=request.user)
    business = CustomerProfile.objects.filter(user=request.user).first()
    context = {
        'orders': order,
        'business': business,
    }
    return render(request, 'account.html', context)

def signup(request):
    if request.method == 'POST':
        form = CustomSignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = CustomSignupForm()
    return render(request, 'registration/signup.html', {'form': form})

# for messages
def make_message(request):
    """ Handle the contact form submission """

    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            contact = form.save(commit=False)
            contact.user = request.user
            contact.save()
            contact = {'contact': Message.objects.filter(user=request.user)}
            return render(request, 'contact.html', contact)
        else:
            return render(request, 'contact.html', {'contact': form})

    else:
        form = MessageForm()
        return render(request, 'contact.html', {'contact': form})

# for orders
def orders(request):
    order = Order.objects.filter(user=request.user)
    context = {
        'orders': order
    }
    return render(request, 'orders.html', context)

def make_order(request):
    """ Handle the order form submission """

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.save()
            business = CustomerProfile.objects.filter(user=request.user).first()
            context = {
                'orders': Order.objects.filter(user=request.user),
                'business': business
            }
            return render(request, 'account.html', context)
        else:
            # Show form errors in the template
            return render(request, 'orders.html', {'orders': form})
    else:
        form = OrderForm()
        return render(request, 'orders.html', {'orders': form})
    
# for reviews
def reviews(request):
    """ handle reviews page """
    reviews = Reviews.objects.all()
    if request.user.is_authenticated:
        user_reviews = Reviews.objects.filter(user=request.user)
    if reviews.exists():
        average_rating = reviews.aggregate(avg_rating=Avg('rating'))['avg_rating']
        if request.user.is_authenticated:
            context = {
                'reviews': reviews,
                'overall_rating': round(average_rating, 1) if average_rating is not None else 0,
                'total_reviews': reviews.count(),
                'user_reviews': user_reviews,
            }
        else:
            context = {
                'reviews': reviews,
                'overall_rating': round(average_rating, 1) if average_rating is not None else 0,
                'total_reviews': reviews.count(),
            }
        return render(request, 'reviews.html', context)
    return render(request, 'reviews.html')

def make_review(request):
    """ handle making reviews from user """

    if request.method == 'POST':
        if request.user.is_authenticated:
            name = request.POST.get('name')
            main_content = request.POST.get('content')
            rating = int(request.POST.get('rating', 0))
            
            review = Reviews.objects.create(
                user=request.user,
                name=name,
                main_content=main_content,
                rating=rating
            )
        messages.success(request, 'Thank you for your review!')
        return redirect('reviews')


@require_POST
def assistant_api(request):
    if not settings.GROQ_API_KEY:
        return JsonResponse({'error': 'Assistant API key is not configured.'}, status=500)

    try:
        payload = json.loads(request.body or '{}')
    except json.JSONDecodeError:
        payload = {}

    # Support both JSON payload (assistant.js) and form fields (legacy usage).
    user_message = str(
        payload.get('message')
        or request.POST.get('message')
        or request.POST.get('letter')
        or ''
    ).strip()
    extra_context = str(
        payload.get('context')
        or request.POST.get('wishlist')
        or ''
    ).strip()

    if not user_message:
        return JsonResponse({'error': 'Message is required.'}, status=400)

    # handle different intent function for logged in users and logged out.
    # this is to prevent accessing pages that will throw errors
    if request.user.is_authenticated:
        intent, confidence = classify_intent_loggedin(user_message)
    else:
        intent, confidence = classify_intent_not_loggedin(user_message)
    suggested_route = INTENT_ROUTE_MAP.get(intent)
    show_navigation = confidence >= 0.7 and suggested_route is not None
    cta_label = INTENT_CTA_LABELS.get(intent, 'Open Page')

    system_context = (
        'You are an AI assistant embedded in a website to help users navigate and find '
        "information. Keep responses concise, practical, and under 250 characters. please don't make up services or prices, just tell them to click the button below, if it isn't what they are looking for they can refine their input"
    )

    if confidence < 0.7:
        system_context += ' If the request is ambiguous, ask one short clarifying question.'

    prompt = f"{system_context}\n\n"
    if extra_context:
        prompt += f"Additional context: {extra_context}\n\n"
    prompt += f"User: {user_message}\nAssistant:"

    if confidence >= 0.7:
        try:
            client = OpenAI(
                api_key=settings.GROQ_API_KEY,
                base_url='https://api.groq.com/openai/v1',
            )

            response = client.responses.create(
                input=prompt,
                model=settings.GROQ_MODEL,
            )
            assistant_text = (response.output_text or '').strip()

            if not assistant_text:
                return JsonResponse({'error': 'Empty response from assistant API.'}, status=502)

            return JsonResponse({
                'response': assistant_text,
                'intent': intent,
                'confidence': confidence,
                'suggested_route': suggested_route,
                'show_navigation': show_navigation,
                'cta_label': cta_label,
            })
        except Exception as exc:
            return JsonResponse({'error': f'Assistant request failed: {str(exc)}'}, status=502)
    else:
        return JsonResponse({
                'response': 'We only provide page navigation right now - could you give us more context for what you are looking for?',
                'intent': intent,
                'confidence': confidence,
                'suggested_route': suggested_route,
                'show_navigation': show_navigation,
                'cta_label': cta_label,
            })

    