# تقرير مفصل: نظام رفع الورقة وترشيح المجلة
# Detailed Report: Paper Upload & Journal Nomination System

## 📋 ملخص المشكلة | Problem Summary

المستخدم غير قادر على عمل "Nominate Journal" (ترشيح مجلة) من واجهة SuperAdminDashboard. على الرغم من وجود Backend endpoint، لا يوجد Frontend UI لاستخدامه.

---

## 🔍 التحليل الحالي | Current Analysis

### 1. Backend Status (✅ موجود ومكتمل)

**Endpoint موجود:**
- URL: `POST /api/v1/admin/articles/<slug:slug>/nominate-journal/`
- View: `AdminArticleNominateJournalView` في `api/v1/views_admin.py`
- Serializer: `NominateArticleSerializer` في `api/v1/admin_serializers.py`
- Service: `ArticleWorkflowService.nominate_journal` في `apps/articles/services.py`

**كيف يعمل الترشيح حالياً:**
```python
# في ArticleCreateView (عند رفع ورقة جديدة)
recommended_journals = ArticleWorkflowService.recommend_journals(article)
if recommended_journals:
    article.nominated_journal = recommended_journals[0]  # تلقائي
    article.save(update_fields=['nominated_journal'])
```

**الخدمة اليدوية (للأدمن):**
```python
# في AdminArticleNominateJournalView
def post(self, request, slug):
    article = get_object_or_404(Article, slug=slug)
    serializer = NominateArticleSerializer(data=request.data, context={'request': request, 'article': article})
    serializer.is_valid(raise_exception=True)
    updated_article = serializer.save()  # يستدعي ArticleWorkflowService.nominate_journal
```

### 2. Frontend Status (❌ ناقص)

**المشكلة:**
- لا يوجد UI في `SuperAdminDashboard.jsx` لترشيح مجلة
- لا يوجد endpoint في `baseApi.js` لاستدعاء `admin/articles/<slug>/nominate-journal/`
- المستخدم لا يستطيع اختيار مجلة يدوياً

---

## 🎯 من يقوم بترشيح المجلة؟ | Who Nominates Journals?

### السيناريو الحالي (تلقائي):
1. **المستخدم** يرفع ورقة من `ManuscriptSubmission.jsx`
2. **النظام** يختار تلقائياً أول مجلة موصى بها
3. **لا يوجد تدخل يدوي** من المستخدم أو الأدمن

### السيناريو المطلوب (يدوي):
1. **المستخدم** يرفع ورقة → النظام يقترح مجلات (تلقائي)
2. **الأدمن** يستطيع تغيير المجلة المترشحة من SuperAdminDashboard
3. **المراجع (Reviewer)** يستطيع ترشيح مجلة من واجهته (إذا وجدت)

---

## 📝 خطة الإصلاح | Fix Plan

### الخطوة 1: إضافة Endpoint إلى baseApi.js
```javascript
// في src/api/baseApi.js
nominateJournal: builder.mutation({
  query: ({ slug, journal_id }) => ({
    url: `admin/articles/${slug}/nominate-journal/`,
    method: 'POST',
    body: { journal_id },
  }),
  invalidatesTags: ['Articles'],
}),
```

### الخطوة 2: إضافة UI إلى SuperAdminDashboard
```jsx
// في SuperAdminDashboard.jsx - تب "Articles"
// لكل ورقة status='under_review' أو 'nominated':
// - عرض قائمة المجلات المتاحة
// - زر "Nominate Journal" يفتح modal لاختيار المجلة
// - عرض المجلة المترشحة حالياً (إذا وجدت)
```

### الخطوة 3: إضافة Modal لاختيار المجلة
```jsx
// مكون جديد: NominateJournalModal
// - قائمة المجلات مع impact_factor و publication_type
// - بحث وتصفية
// - تأكيد قبل الترشيح
```

---

## 🔄 سير عمل رفع الورقة المثالي | Ideal Paper Upload Workflow

### المرحلة 1: رفع الورقة (المستخدم)
```
1. المستخدم يذهب إلى ManuscriptSubmission
2. يملأ:
   - Research Information (title, abstract, category, keywords, location)
   - Submission Formatting (font, margins, figures) ← NEW
   - Manuscript Upload (PDF)
3. يضغط "Submit Manuscript for Academic Review"
4. Backend:
   - يخلق Article مع status='under_review'
   - يستدعي recommend_journals(article)
   - يحدد nominated_journal تلقائياً (أول مجلة موصى بها)
   - يمنح 10 نقاط للمستخدم
5. Frontend:
   - يعرض رسالة نجاح
   - يعرض المجلات الموصى بها (3 مجلات)
   - يعرض المجلة المترشحة حالياً
```

### المرحلة 2: المراجعة (المراجع/الأدمن)
```
1. الأدمن يرى الورقة في SuperAdminDashboard (تب "Articles")
2. يستطيع:
   - تعيين مراجع (Assign Reviewer)
   - ترشيح مجلة مختلفة (Nominate Journal) ← MISSING
   - نشر الورقة (Publish)
3. المراجع يستطيع:
   - كتابة تقييم
   - ترشيح مجلة (إذا وجدت واجهة)
```

### المرحلة 3: الترشيح والنشر
```
1. بعد الترشيح:
   - status يصبح 'nominated'
   - nominated_journal محدد
   - subsidy_status يُحدد بناءً على النقاط
2. بعد النشر:
   - status يصبح 'published'
   - published_at يُحدد
   - الورقة تظهر للجمهور
```

---

## 🛠️ المهام المطلوبة | Required Tasks

### Backend (✅ مكتمل)
- [x] AdminArticleNominateJournalView
- [x] NominateArticleSerializer
- [x] ArticleWorkflowService.nominate_journal
- [x] URL route

### Frontend (❌ ناقص)
- [ ] إضافة nominateJournal mutation إلى baseApi.js
- [ ] إضافة UI لترشيح المجلة في SuperAdminDashboard
- [ ] إضافة Modal لاختيار المجلة
- [ ] عرض المجلة المترشحة حالياً في بطاقة الورقة
- [ ] إضافة زر "Change Nominated Journal"

### Testing
- [ ] اختبار ترشيح مجلة من SuperAdminDashboard
- [ ] اختبار تأثير الترشيح على status الورقة
- [ ] اختبار الترشيح على ورقة status='under_review'
- [ ] اختبار الترشيح على ورقة status='nominated' (تغيير المجلة)

---

## 📊 مخطط البيانات | Data Flow

```
User (ManuscriptSubmission)
  ↓ POST /articles/ (FormData)
Backend (ArticleCreateView)
  ↓ create article (status='under_review')
  ↓ recommend_journals(article)
  ↓ nominated_journal = journals[0] (auto)
  ↓ award_points(user, 'submit_article')
  ↓ Response with article data
Frontend (Success State)
  ↓ Display recommended journals
  ↓ Display nominated journal

Admin (SuperAdminDashboard)
  ↓ POST /admin/articles/<slug>/nominate-journal/ (journal_id)
Backend (AdminArticleNominateJournalView)
  ↓ validate article status
  ↓ validate formatting
  ↓ nominated_journal = selected_journal
  ↓ status = 'nominated'
  ↓ refresh_subsidy_status
  ↓ Response with updated article
Frontend (Update UI)
  ↓ Show new nominated journal
  ↓ Update status badge
```

---

## 🎨 واجهة المستخدم المقترحة | Proposed UI

### في SuperAdminDashboard (تب "Articles")
لكل ورقة:
```
┌─────────────────────────────────────────┐
│ Article Title                            │
│ Status: Under Review | Nominated        │
│ Author: John Doe                         │
│                                         │
│ Nominated Journal: [Journal Name]       │
│ [Change Journal] [View Details]         │
│                                         │
│ Actions:                                │
│ [Assign Reviewer] [Nominate Journal]     │
│ [Publish] [Delete]                      │
└─────────────────────────────────────────┘
```

### Modal لترشيح المجلة
```
┌─────────────────────────────────────────┐
│ Nominate Journal for Article            │
│                                         │
│ Search: [__________]                    │
│                                         │
│ Available Journals:                     │
│ ☐ Nature (IF: 49.9) - Open Access       │
│ ☐ Science (IF: 47.7) - Subscription    │
│ ☐ Cell (IF: 45.5) - Open Access        │
│                                         │
│ [Cancel] [Confirm Nomination]           │
└─────────────────────────────────────────┘
```

---

## ⚠️ ملاحظات مهمة | Important Notes

1. **الترشيح التلقائي vs اليدوي:**
   - الترشيح التلقائي يحدث عند رفع الورقة
   - الترشيح اليدوي يمكن للأدمن تغييره لاحقاً
   - يجب الحفاظ على الترشيح التلقائي كافتراضي

2. **الصلاحيات:**
   - فقط الأدمن (is_staff=True) يستطيع ترشيح مجلة يدوياً
   - المستخدم العادي لا يستطيع تغيير المجلة بعد الرفع

3. **التحقق:**
   - يجب التحقق من أن status الورقة 'under_review' أو 'nominated'
   - يجب التحقق من تنسيق الورقة مقابل متطلبات المجلة
   - يجب تحديث subsidy_status بعد الترشيح

4. **الإشعارات:**
   - يجب إرسال إشعار للمستخدم عند تغيير المجلة المترشحة
   - يجب إرسال إشعار عند نشر الورقة

---

## 📅 الجدول الزمني | Timeline

- **اليوم 1:** إضافة endpoint إلى baseApi.js
- **اليوم 1:** إضافة UI بسيط في SuperAdminDashboard
- **اليوم 2:** إضافة Modal لاختيار المجلة
- **اليوم 2:** اختبار الوظيفة
- **اليوم 3:** تحسين UI وإضافة الإشعارات
