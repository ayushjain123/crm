from django.core.mail import send_mail
from django.shortcuts import render, redirect, reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.views import generic
from agents.mixins import OrganisorAndLoginRequiredMixin
from .models import Lead, Agent, Category
from .forms import (
    LeadForm,
    LeadModelForm,
    CustomUserCreationForm,
    AssignAgentForm,
    LeadCategoryUpdateForm
)


class SignupView(generic.CreateView):
    template_name="registration/signup.html"
    form_class= CustomUserCreationForm

    def get_success_url(self):
        return reverse("login")

class LandingPageView(generic.TemplateView):
    template_name='landing.html'

def landing(request):
    return render(request,'landing.html')

class LeadListView(LoginRequiredMixin, generic.ListView):
    template_name='lead_list.html'
    context_object_name= "leads"

    def get_queryset(self):
        user = self.request.user

        #initial queryset for leads for the organisation
        if user.is_organisor:
            queryset= Lead.objects.filter(organisation= user.userprofile, agent__isnull=False)
        else:
            queryset= Lead.objects.filter(organisation= user.agent.organisation, agent__isnull=False)
            #filter for logged in agent
            queryset= queryset.filter(agent__user = user)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(LeadListView, self).get_context_data(**kwargs)
        user = self.request.user

        if user.is_organisor:
            queryset= Lead.objects.filter(
            organisation= user.userprofile,
            agent__isnull=True
            )
            context.update({
                "unassigned_leads": queryset
            })
        return context

def lead_list(request):
    leads=Lead.objects.all()
    context={
        'leads':leads
    }
    return render(request,'lead_list.html',context)

class LeadDetailView(LoginRequiredMixin, generic.DetailView):
    template_name='lead_detail.html'
    context_object_name= "lead"


    def get_queryset(self):
        user = self.request.user

        #initial queryset for leads for the organisation
        if user.is_organisor:
            queryset= Lead.objects.filter(organisation= user.userprofile)
        else:
            queryset= Lead.objects.filter(organisation= user.agent.organisation)
            #filter for logged in agent
            queryset= queryset.filter(agent__user = user)
        return queryset


def lead_detail(request, pk):
    lead=Lead.objects.get(id=pk)
    context={
        'lead': lead
    }
    return render(request,'lead_detail.html',context)

class LeadCreateView(OrganisorAndLoginRequiredMixin, generic.CreateView):
    template_name='lead_create.html'
    form_class= LeadModelForm

    def get_success_url(self):
        return reverse("lead_list")

    def form_valid(self, form):
        lead = form.save(commit=False)
        lead.organisation = self.request.user.userprofile
        lead.save()
        send_mail(
            subject="Created",
            message="Lead Added",
            from_email="test@test.com",
            recipient_list=["test2@test.com"]
        )
        return super(LeadCreateView, self).form_valid(form)


def lead_create(request):
    form =LeadModelForm()
    if request.method=='POST':
        form=LeadModelForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lead_list')
    context={
        'form': form
    }
    return render(request,'lead_create.html',context)

class LeadUpdateView(OrganisorAndLoginRequiredMixin, generic.UpdateView):
    template_name='lead_update.html'
    form_class= LeadModelForm

    def get_queryset(self):
        user = self.request.user
        #initial queryset for leads for the organisation
        if user.is_organisor:
            return Lead.objects.filter(organisation= user.userprofile)

    def get_success_url(self):
        return reverse("lead_list")



def lead_update(request, pk):
    lead= Lead.objects.get(id=pk)
    form =LeadModelForm(instance=lead)
    if request.method=='POST':
        form=LeadModelForm(request.POST,instance=lead)
        if form.is_valid():
            form.save()
            return redirect('lead_list')

    context={
        'form': form,
        'lead': lead
    }
    return render(request,'lead_update.html',context)

class LeadDeleteView(OrganisorAndLoginRequiredMixin, generic.DeleteView):
    template_name='lead_delete.html'
    form_class= LeadModelForm


    def get_success_url(self):
        return reverse("lead_list")

    def get_queryset(self):
        user = self.request.user
        #initial queryset for leads for the organisation
        if user.is_organisor:
            return Lead.objects.filter(organisation= user.userprofile)


def lead_delete(request, pk):
    lead= Lead.objects.get(id=pk)
    lead.delete()
    return redirect('lead_list')

class AssignAgentView(OrganisorAndLoginRequiredMixin, generic.FormView):
    template_name = "assign_agent.html"
    form_class = AssignAgentForm

    def get_form_kwargs(self, **kwargs):
        kwargs = super(AssignAgentView, self).get_form_kwargs(**kwargs)
        kwargs.update({
            "request": self.request
        })
        return kwargs

    def get_success_url(self):
        return reverse("lead_list")

    def form_valid(self, form):
        agent = form.cleaned_data["agent"]
        lead = Lead.objects.get(id=self.kwargs["pk"])
        lead.agent = agent
        lead.save()
        return super(AssignAgentView, self).form_valid(form)


class CategoryListView(LoginRequiredMixin, generic.ListView):
    template_name = "category_list.html"
    context_object_name = "category_list"

    def get_context_data(self, **kwargs):
        context = super(CategoryListView, self).get_context_data(**kwargs)
        user = self.request.user

        if user.is_organisor:
            queryset = Lead.objects.filter(
                organisation=user.userprofile
            )
        else:
            queryset = Lead.objects.filter(
                organisation=user.agent.organisation
            )

        context.update({
            "unassigned_lead_count": queryset.filter(category__isnull=True).count()
        })
        return context

    def get_queryset(self):
        user = self.request.user
        # initial queryset of leads for the entire organisation
        if user.is_organisor:
            queryset = Category.objects.filter(
                organisation=user.userprofile
            )
        else:
            queryset = Category.objects.filter(
                organisation=user.agent.organisation
            )
        return queryset

class CategoryDetailView(LoginRequiredMixin, generic.DetailView):
    template_name = "category_detail.html"
    context_object_name = "category"

    def get_queryset(self):
        user = self.request.user
        # initial queryset of leads for the entire organisation
        if user.is_organisor:
            queryset = Category.objects.filter(
                organisation=user.userprofile
            )
        else:
            queryset = Category.objects.filter(
                organisation=user.agent.organisation
            )
        return queryset

class LeadCategoryUpdateView(LoginRequiredMixin, generic.UpdateView):
    template_name='category_update.html'
    form_class= LeadCategoryUpdateForm

    def get_queryset(self):
        user = self.request.user
        if user.is_organisor:
            queryset= Lead.objects.filter(organisation= user.userprofile)
        else:
            queryset= Lead.objects.filter(organisation= user.agent.organisation)
            #filter for logged in agent
            queryset= queryset.filter(agent__user = user)
        return queryset

    def get_success_url(self):
        return reverse("lead_detail", kwargs={"pk": self.get_object().id})


# def lead_update(request, pk):
#     lead= Lead.objects.get(id=pk)
    # form =LeadForm()
    # if request.method=='POST':
    #     form=LeadForm(request.POST)
    #     if form.is_valid():
    #         first_name=form.cleaned_data['first_name']
    #         last_name=form.cleaned_data['last_name']
    #         age=form.cleaned_data['age']
    #
    #         lead.first_name=first_name
    #         lead.last_name=last_name
    #         lead.age=age
    #
    #         lead.save()
    #
    #         return redirect('/')
    # context={
    #     'form': form,
    #     'lead': lead
    # }
    # return render(request,'lead_update.html',context)


# def lead_create(request):
    # form =LeadForm()
    # if request.method=='POST':
    #     form=LeadForm(request.POST)
    #     if form.is_valid():
    #         first_name=form.cleaned_data['first_name']
    #         last_name=form.cleaned_data['last_name']
    #         age=form.cleaned_data['age']
    #         agent=Agent.objects.first()
    #
    #         Lead.objects.create(
    #             first_name=first_name,
    #             last_name=last_name,
    #             age=age,
    #             agent=agent
    #         )
    #         return redirect('/')
    # context={
    #     'form': form
    # }
#     return render(request,'lead_create.html',context)
