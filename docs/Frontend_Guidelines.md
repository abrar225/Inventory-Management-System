# FRONTEND DESIGN SYSTEM & UI GUIDELINES

## Inventory Management System (IMS)

Version: 1.0

Depends On:

* PRD v1.0
* App Flow v1.0
* Tech Stack v1.0

---

# 1. Design Philosophy

The UI must communicate:

* Professional
* Clean
* Enterprise-grade
* Data-focused
* Minimal
* Modern
* Premium
* Fast
* Organized
* Trustworthy

The interface should prioritize readability and efficient workflows over decorative visuals.

---

# 2. Visual Inspiration

Reference products:

* Linear
* Stripe Dashboard
* Vercel Dashboard
* Supabase
* Clerk
* Notion
* Attio
* Arc Browser Settings
* GitHub

Avoid:

* Glass-heavy designs
* Neumorphism
* Cartoon illustrations
* Loud gradients
* Excessive animations
* Rounded "bubble" interfaces
* Material Design clones

---

# 3. Design Language

Keywords

```text
Minimal
Elegant
Soft
Professional
Premium
Balanced
Structured
Modern Enterprise
```

---

# 4. Layout Structure

Desktop Layout

```text
+------------------------------------------------------+
| Header                                               |
+-----------+------------------------------------------+
| Sidebar   |                                          |
|           |                                          |
|           |          Main Content                    |
|           |                                          |
|           |                                          |
+-----------+------------------------------------------+
```

Sidebar

Fixed

Width

```text
280px
```

Header

Height

```text
72px
```

Content

Maximum Width

```text
1600px
```

Centered

---

# 5. Grid System

Desktop

12-column CSS Grid

Gap

```text
24px
```

Tablet

8 columns

Mobile

4 columns

---

# 6. Spacing System

Use an 8-point spacing scale exclusively.

| Token | Value |
| ----- | ----- |
| xs    | 4px   |
| sm    | 8px   |
| md    | 16px  |
| lg    | 24px  |
| xl    | 32px  |
| 2xl   | 48px  |
| 3xl   | 64px  |
| 4xl   | 96px  |

Never use arbitrary spacing values.

---

# 7. Border Radius

Small

```text
8px
```

Medium

```text
12px
```

Large

```text
16px
```

Cards

```text
20px
```

Never exceed

```text
24px
```

---

# 8. Color Palette

## Primary

```text
#2563EB
```

Blue

---

Primary Hover

```text
#1D4ED8
```

---

Background

```text
#F8FAFC
```

---

Surface

```text
#FFFFFF
```

---

Sidebar

```text
#FFFFFF
```

---

Text Primary

```text
#0F172A
```

---

Text Secondary

```text
#64748B
```

---

Border

```text
#E2E8F0
```

---

Success

```text
#16A34A
```

---

Warning

```text
#F59E0B
```

---

Danger

```text
#DC2626
```

---

Info

```text
#0EA5E9
```

---

Low Stock

```text
#F97316
```

---

Out of Stock

```text
#EF4444
```

---

Card Shadow

```text
0 6px 18px rgba(15,23,42,.06)
```

---

# 9. Dark Mode

Supported

Yes

Dark Background

```text
#0F172A
```

Surface

```text
#1E293B
```

Text

```text
#F8FAFC
```

Border

```text
#334155
```

---

# 10. Typography

Font

```text
Inter
```

Fallback

```text
system-ui
```

---

Heading 1

40px

700

---

Heading 2

32px

700

---

Heading 3

24px

600

---

Heading 4

20px

600

---

Body Large

18px

500

---

Body

16px

400

---

Small

14px

400

---

Caption

12px

500

---

Line Height

1.5

---

Never use more than three font weights on a page.

---

# 11. Iconography

Library

Heroicons

Size

16

20

24

32

Style

Outline

Filled only for active states.

---

# 12. Buttons

Primary

Blue background

White text

Height

```text
44px
```

Radius

12px

---

Secondary

White

Gray Border

---

Danger

Red

---

Ghost

Transparent

---

Icon Button

Square

40px

---

Button animation

150ms ease

---

# 13. Forms

Label above input

Always.

Input Height

```text
48px
```

Radius

12px

Padding

16px

Focus

Blue border

Blue glow

---

Validation

Inline

Never use alert popups.

---

# 14. Tables

Professional enterprise tables.

Header

Sticky

Height

56px

Row

56px

Hover

Light Gray

Zebra

No

---

Columns

Resizable (future)

---

Pagination

Bottom Right

---

Actions

Right aligned

---

# 15. Cards

Radius

20px

Padding

24px

White background

Soft shadow

No colored cards except metrics.

---

# 16. Dashboard

Top Section

```text
4 KPI Cards
```

Second Row

```text
Charts
```

Third Row

```text
Low Stock

Recent Sales

Recent Purchases
```

Fourth

Quick Actions

---

# 17. KPI Cards

Display

Large Number

Small Label

Tiny Trend

Icon

Top Right

Hover

Lift

4px

---

# 18. Charts

Library

Chart.js

Style

Minimal

Rounded bars

Thin grid lines

No heavy colors

---

# 19. Navigation

Sidebar

Collapsed

Desktop

Expanded

Mobile

Slide-in drawer

Current Page

Blue indicator

Bold text

---

# 20. Breadcrumb

Example

Dashboard

>

Products

>

iPhone

---

Always visible.

---

# 21. Search

Global search

Header

Rounded input

Live search

HTMX

Debounced

300ms

---

# 22. Filters

Contained inside cards.

Never floating.

---

# 23. Modals

Centered

Blur background

Width

600px

Escape closes

Click outside closes

Danger actions require confirmation.

---

# 24. Notifications

Toast

Top Right

Auto dismiss

4 seconds

Icons

Required

---

# 25. Empty States

Illustration

Minimal line illustration

Title

Description

Primary CTA

---

Example

"No products yet"

Button

Create Product

---

# 26. Loading States

Skeleton loaders

No spinning page loaders.

---

# 27. Animations

Duration

150–250ms

Use

Fade

Scale

Slide

Hover

Never bounce.

Never rotate.

Never flashy.

---

# 28. Mobile Responsive

Desktop

1600+

Laptop

1440

Tablet

1024

Mobile

768

Small Mobile

375

---

Sidebar

Desktop

Fixed

Tablet

Collapsible

Mobile

Drawer

---

Tables

Become stacked cards below 768px.

---

# 29. Accessibility

Minimum contrast ratio

4.5:1

Keyboard navigation

Required

Visible focus rings

Required

ARIA labels

Required

---

# 30. Product Images

Aspect Ratio

1:1

Rounded

12px

Placeholder if missing

Required

---

# 31. Dashboard Widgets

Cards

Charts

Recent Activity

Low Stock

Top Products

Revenue Summary

Inventory Value

Quick Actions

---

# 32. Visual Hierarchy

Every page

```text
Title

↓

Subtitle

↓

Actions

↓

Filters

↓

Content
```

---

# 33. Component Library

Every UI element must be reusable.

Components

```text
Button

Card

Modal

Drawer

Input

Textarea

Checkbox

Radio

Badge

Avatar

Dropdown

Pagination

Breadcrumb

Table

Chart

Search

Toast

Alert

Skeleton

Tabs

Empty State

KPI Card

Stat Card

Confirmation Dialog

File Upload

Image Preview
```

---

# 34. Tailwind Rules

Never use inline styles.

Never use arbitrary values unless absolutely necessary.

Prefer semantic utility groupings.

Extract repeated patterns into reusable components.

---

# 35. UX Rules

Every destructive action requires confirmation.

Every form has Cancel + Save.

Every page has breadcrumbs.

Every table has search.

Every list has pagination.

Every create form redirects to detail page after success.

Errors appear inline.

Success uses toast.

---

# 36. Visual Consistency Rules

* One primary color.
* One font family.
* One spacing system.
* One border radius scale.
* One shadow scale.
* One icon library.
* One animation timing system.
* No mixed design styles.

---

# 37. Dashboard Wireframe

```text
┌─────────────────────────────────────────────────────────────────────┐
│ Header                                      Search    Profile        │
├──────────────┬──────────────────────────────────────────────────────┤
│              │  KPI Cards (4)                                      │
│              ├──────────────────────────────────────────────────────┤
│              │  Sales Chart        Purchase Chart                  │
│ Sidebar      ├──────────────────────────────────────────────────────┤
│              │  Low Stock      Recent Sales      Recent Purchases   │
│              ├──────────────────────────────────────────────────────┤
│              │  Top Products      Inventory Value                  │
│              └──────────────────────────────────────────────────────┘
```

---

# 38. Page Template Structure

Every page follows the exact same structure:

```text
Header

↓

Breadcrumb

↓

Page Title

↓

Primary Actions

↓

Filters

↓

Main Content

↓

Pagination

↓

Footer
```

---

# 39. UI Quality Checklist

Before any page is considered complete, it **must** satisfy the following:

* Responsive from 375px to 1600px+
* Keyboard accessible
* Supports dark mode
* Uses reusable components only
* No duplicated UI patterns
* All forms validated
* Empty states implemented
* Loading skeletons implemented
* Success and error toasts implemented
* Consistent spacing, typography, and colors
* No layout shift during loading
* Lighthouse Performance ≥ 90
* Lighthouse Accessibility ≥ 95
* Lighthouse Best Practices ≥ 95

---

## **One major improvement I'd make before Document 5 (Backend Schema)**

If this were a real enterprise application, I would **introduce a Domain-Driven Design (DDD)-inspired module boundary**, even while staying within standard Django.

Instead of treating each app as only CRUD, define clear domain ownership:

* **accounts** → users, roles, permissions
* **catalog** → products, categories, suppliers
* **inventory** → stock ledger, adjustments, movements
* **sales** → invoices, sale items
* **purchasing** → purchases, purchase items
* **reporting** → read models and analytics
* **audit** → immutable audit events
* **common** → shared utilities, mixins, validators

