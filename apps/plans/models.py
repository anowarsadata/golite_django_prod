from django.db import models
from django.utils.text import slugify


class Plan(models.Model):
    SIM_TYPE_CHOICES = (
        ('psim', 'pSIM'),
        ('esim', 'eSIM'),
    )

    # ========================
    # BASIC INFO
    # ========================
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)

    short_description = models.CharField(
        max_length=255, blank=True, null=True
    )
    description = models.TextField(
        blank=True, null=True
    )

    # ========================
    # PRICING
    # ========================
    price = models.DecimalField(max_digits=10, decimal_places=2)
    sale_price = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )

    duration_days = models.PositiveIntegerField(default=30)

    sim_type = models.CharField(
        max_length=20, choices=SIM_TYPE_CHOICES
    )

    # ========================
    # FLAGS
    # ========================
    is_popular = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    # ========================
    # SEO – META
    # ========================
    meta_title = models.CharField(max_length=255, blank=True, null=True)
    meta_description = models.CharField(max_length=255, blank=True, null=True)
    meta_keywords = models.CharField(max_length=255, blank=True, null=True)
    canonical_url = models.URLField(blank=True, null=True)

    # ========================
    # SEO – OPEN GRAPH
    # ========================
    og_title = models.CharField(max_length=255, blank=True, null=True)
    og_description = models.CharField(max_length=255, blank=True, null=True)
    og_image = models.ImageField(upload_to='plans/seo/', blank=True, null=True)
    og_type = models.CharField(max_length=50, default='product')

    # ========================
    # SEO – TWITTER
    # ========================
    twitter_title = models.CharField(max_length=255, blank=True, null=True)
    twitter_description = models.CharField(max_length=255, blank=True, null=True)
    twitter_image = models.ImageField(upload_to='plans/seo/', blank=True, null=True)

    # ========================
    # SEO – SCHEMA
    # ========================
    schema_markup = models.JSONField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['price']

    def __str__(self):
        return self.name

    # ========================
    # AUTO LOGIC
    # ========================
    def save(self, *args, **kwargs):

        # Auto-generate unique slug
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1

            while Plan.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        # Auto SEO fallback (only if empty)
        if not self.meta_title:
            self.meta_title = self.name

        if not self.meta_description:
            self.meta_description = self.short_description or self.description

        if not self.og_title:
            self.og_title = self.meta_title

        if not self.og_description:
            self.og_description = self.meta_description

        if not self.twitter_title:
            self.twitter_title = self.meta_title

        if not self.twitter_description:
            self.twitter_description = self.meta_description

        super().save(*args, **kwargs)

    @property
    def final_price(self):
        return self.sale_price if self.sale_price else self.price


class PlanFeature(models.Model):
    plan = models.ForeignKey(
        Plan, related_name='features', on_delete=models.CASCADE
    )
    title = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.plan.name} - {self.title}"
