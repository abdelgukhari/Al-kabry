# E-Commerce Database Design Diagram

## Database Schema Overview

This document contains the complete Entity-Relationship (ER) diagram for the E-commerce Alkabry project.

---

## Complete ER Diagram (Mermaid Format)

```mermaid
erDiagram
    User {
        int id PK
        string username
        string email UK
        string first_name
        string last_name
        string phone
        date date_of_birth
        string address
        string city
        string country
        string zip_code
        boolean is_staff
        boolean is_active
        boolean is_superuser
        datetime last_login
        datetime date_joined
        datetime created_at
        datetime updated_at
    }

    Category {
        int id PK
        string name
        string slug UK
        int parent FK
        text description
        string image
        boolean is_active
        datetime created_at
    }

    Tag {
        int id PK
        string name UK
        string slug UK
    }

    Product {
        int id PK
        string name
        string slug UK
        text description
        string short_description
        decimal price
        decimal compare_price
        decimal cost_price
        string sku UK
        int stock
        boolean is_available
        int category FK
        string brand
        string color
        string size
        string material
        string image
        float avg_rating
        int rating_count
        int views_count
        int purchases_count
        boolean is_featured
        boolean is_active
        datetime created_at
        datetime updated_at
    }

    ProductImage {
        int id PK
        int product FK
        string image
        string alt_text
        boolean is_primary
        datetime created_at
    }

    Review {
        int id PK
        int product FK
        int user FK
        int rating
        string title
        text comment
        boolean is_approved
        datetime created_at
        datetime updated_at
    }

    Cart {
        int id PK
        int user O2O
        string session_key
        datetime created_at
        datetime updated_at
    }

    CartItem {
        int id PK
        int cart FK
        int product FK
        int quantity
        datetime created_at
        datetime updated_at
    }

    Order {
        int id PK
        int user FK
        string order_number UK
        string status
        string payment_status
        string payment_method
        decimal subtotal
        decimal shipping_cost
        decimal tax
        decimal discount
        decimal total
        string shipping_address
        string shipping_city
        string shipping_country
        string shipping_zip_code
        string shipping_phone
        text notes
        string tracking_number
        datetime created_at
        datetime updated_at
    }

    OrderItem {
        int id PK
        int order FK
        int product FK
        string product_name
        string product_sku
        decimal price
        int quantity
        datetime created_at
    }

    RecommendationEvent {
        int id PK
        int user FK
        string session_key
        string algorithm
        string event_type
        int product FK
        int position
        decimal revenue
        datetime created_at
    }

    UserInteraction {
        int id PK
        int user FK
        string session_key
        int product FK
        int target_product FK
        string interaction_type
        float weight
        string algorithm_used
        datetime created_at
    }

    AlgorithmMetrics {
        int id PK
        string algorithm
        date date
        int impressions
        int clicks
        int add_to_carts
        int purchases
        float ctr
        float conversion_rate
        decimal total_revenue
        decimal avg_order_value
        float precision_at
        float recall
        float f1_score
        float ndcg
        float diversity
        float coverage
        datetime created_at
        datetime updated_at
    }

    ComparisonReport {
        int id PK
        string title
        text description
        json metrics_data
        json ranking
        string winner
        date start_date
        date end_date
        boolean is_final
        datetime created_at
    }

    Category ||--o{ Category : "has_children"
    Category ||--o{ Product : "contains"
    Product }o--o{ Tag : "has"
    Product ||--o{ ProductImage : "has"
    Product ||--o{ Review : "has"
    User ||--o{ Review : "writes"
    User ||--o| Cart : "owns"
    Cart ||--o{ CartItem : "contains"
    Product ||--o{ CartItem : "added_to_cart"
    User ||--o{ Order : "places"
    Order ||--o{ OrderItem : "contains"
    Product ||--o{ OrderItem : "in_order"
    User ||--o{ RecommendationEvent : "receives"
    Product ||--o{ RecommendationEvent : "recommended_in"
    User ||--o{ UserInteraction : "performs"
    Product ||--o{ UserInteraction : "interacted_with"
    Product ||--o{ UserInteraction : "recommended_as"
```

---

## Simplified Visual ER Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         ACCOUNTS APP                                 │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────────────────────────────────┐                       │
│  │                    USER                  │                       │
│  │──────────────────────────────────────────│                       │
│  │ PK  id              |  email (UK)        │                       │
│  │     username        |  phone             │                       │
│  │     first_name      |  last_name         │                       │
│  │     date_of_birth   |  address           │                       │
│  │     city            |  country           │                       │
│  │     zip_code        |  is_staff          │                       │
│  │     is_active       |  is_superuser      │                       │
│  │     created_at      |  updated_at        │                       │
│  └──────────────────────────────────────────┘                       │
│         │              │              │                             │
│         │              │              │                             │
│         │ OneToOne     │ 1:N          │ 1:N                         │
│         ▼              ▼              ▼                             │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐                        │
│  │   CART   │   │  REVIEW  │   │  ORDER   │                        │
│  └──────────┘   └──────────┘   └──────────┘                        │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────────┐
│                        PRODUCTS APP                                 │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────────────────────────────────┐                       │
│  │                 CATEGORY                 │                       │
│  │──────────────────────────────────────────│                       │
│  │ PK  id              |  name              │                       │
│  │     slug (UK)       |  parent (FK self)  │──┐                    │
│  │     description     |  image             │  │                    │
│  │     is_active       |  created_at        │  │ recursive          │
│  └──────────────────────────────────────────┘  │                    │
│         │                                       └────────────────┐   │
│         │ 1:N                                                    │   │
│         ▼                                                        │   │
│  ┌──────────────────────────────────────────┐                    │   │
│  │                 PRODUCT                  │                    │   │
│  │──────────────────────────────────────────│                    │   │
│  │ PK  id              |  name              │                    │   │
│  │     slug (UK)       |  description       │                    │   │
│  │     price           |  compare_price     │                    │   │
│  │     cost_price      |  sku (UK)          │                    │   │
│  │     stock           |  is_available      │                    │   │
│  │     category (FK)   |  brand             │                    │   │
│  │     color           |  size              │                    │   │
│  │     material        |  image             │                    │   │
│  │     avg_rating      |  rating_count      │                    │   │
│  │     views_count     |  purchases_count   │                    │   │
│  │     is_featured     |  is_active         │                    │   │
│  │     created_at      |  updated_at        │                    │   │
│  └──────────────────────────────────────────┘                    │   │
│         │              │              │                          │   │
│         │ 1:N          │ 1:N          │ M2N                      │   │
│         ▼              ▼              ▼                          │   │
│  ┌──────────────┐ ┌──────────┐   ┌──────────┐                   │   │
│  │PRODUCT_IMAGE │ │  REVIEW  │   │   TAG    │◄────────────────────┘   │
│  └──────────────┘ └──────────┘   └──────────┘                        │
│         │                                                             │
│         │ (alt_text, is_primary)                                     │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────────┐
│                          CART APP                                   │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────────────────────────────────┐                       │
│  │                   CART                   │                       │
│  │──────────────────────────────────────────│                       │
│  │ PK  id              |  user (OneToOne)   │──┐                    │
│  │     session_key     |  created_at        │  │                    │
│  │     updated_at      |                    │  │                    │
│  └──────────────────────────────────────────┘  │                    │
│         │                                       │                    │
│         │ 1:N                                   │                    │
│         ▼                                       │                    │
│  ┌──────────────────────────────────────────┐   │                    │
│  │               CART_ITEM                  │   │                    │
│  │──────────────────────────────────────────│   │                    │
│  │ PK  id              |  cart (FK)         │◄──┘                    │
│  │     product (FK)    |  quantity          │                        │
│  │     created_at      |  updated_at        │                        │
│  └──────────────────────────────────────────┘                        │
│         │                                                             │
│         │ FK (references Product)                                    │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────────┐
│                         ORDERS APP                                  │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────────────────────────────────┐                       │
│  │                  ORDER                   │                       │
│  │──────────────────────────────────────────│                       │
│  │ PK  id              |  user (FK)         │──┐                    │
│  │     order_number(UK)|  status            │  │                    │
│  │     payment_status  |  payment_method    │  │                    │
│  │     subtotal        |  shipping_cost     │  │                    │
│  │     tax             |  discount          │  │                    │
│  │     total           |  shipping_address  │  │                    │
│  │     shipping_city   |  shipping_country  │  │                    │
│  │     shipping_zip    |  shipping_phone    │  │                    │
│  │     notes           |  tracking_number   │  │                    │
│  │     created_at      |  updated_at        │  │                    │
│  └──────────────────────────────────────────┘  │                    │
│         │                                       │                    │
│         │ 1:N                                   │                    │
│         ▼                                       │                    │
│  ┌──────────────────────────────────────────┐   │                    │
│  │               ORDER_ITEM                 │   │                    │
│  │──────────────────────────────────────────│   │                    │
│  │ PK  id              |  order (FK)        │◄──┘                    │
│  │     product (FK)    |  product_name      │                        │
│  │     product_sku     |  price             │                        │
│  │     quantity        |  created_at        │                        │
│  └──────────────────────────────────────────┘                        │
│         │                                                             │
│         │ FK (references Product)                                    │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────────┐
│                     RECOMMENDATIONS APP                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────────────────────────────────┐                       │
│  │        RECOMMENDATION_EVENT              │                       │
│  │──────────────────────────────────────────│                       │
│  │ PK  id              |  user (FK)         │                       │
│  │     session_key     |  algorithm         │                       │
│  │     event_type      |  product (FK)      │                       │
│  │     position        |  revenue           │                       │
│  │     created_at      |                    │                       │
│  └──────────────────────────────────────────┘                       │
│                                                                     │
│  ┌──────────────────────────────────────────┐                       │
│  │          USER_INTERACTION                │                       │
│  │──────────────────────────────────────────│                       │
│  │ PK  id              |  user (FK)         │                       │
│  │     session_key     |  product (FK)      │                       │
│  │     target_product  |  interaction_type  │                       │
│  │     weight          |  algorithm_used    │                       │
│  │     created_at      |                    │                       │
│  └──────────────────────────────────────────┘                       │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────────┐
│                        ANALYTICS APP                                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────────────────────────────────┐                       │
│  │         ALGORITHM_METRICS               │                       │
│  │──────────────────────────────────────────│                       │
│  │ PK  id              |  algorithm         │                       │
│  │     date            |  impressions       │                       │
│  │     clicks          |  add_to_carts      │                       │
│  │     purchases       |  ctr               │                       │
│  │     conversion_rate |  total_revenue     │                       │
│  │     avg_order_value |  precision         │                       │
│  │     recall          |  f1_score          │                       │
│  │     ndcg            |  diversity         │                       │
│  │     coverage        |  created_at        │                       │
│  │     updated_at      |                    │                       │
│  └──────────────────────────────────────────┘                       │
│                                                                     │
│  ┌──────────────────────────────────────────┐                       │
│  │        COMPARISON_REPORT                │                       │
│  │──────────────────────────────────────────│                       │
│  │ PK  id              |  title             │                       │
│  │     description     |  metrics_data(JSON)│                       │
│  │     ranking (JSON)  |  winner            │                       │
│  │     start_date      |  end_date          │                       │
│  │     is_final        |  created_at        │                       │
│  └──────────────────────────────────────────┘                       │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Relationship Matrix

| From Table | Field | To Table | Relationship Type | On Delete |
|------------|-------|----------|-------------------|-----------|
| **Category** | parent | Category | ManyToOne (self-ref) | CASCADE |
| **Product** | category | Category | ManyToOne | SET_NULL |
| **Product** | tags | Tag | ManyToMany | - |
| **ProductImage** | product | Product | ManyToOne | CASCADE |
| **Review** | product | Product | ManyToOne | CASCADE |
| **Review** | user | User | ManyToOne | CASCADE |
| **Cart** | user | User | OneToOne | CASCADE |
| **CartItem** | cart | Cart | ManyToOne | CASCADE |
| **CartItem** | product | Product | ManyToOne | CASCADE |
| **Order** | user | User | ManyToOne | SET_NULL |
| **OrderItem** | order | Order | ManyToOne | CASCADE |
| **OrderItem** | product | Product | ManyToOne | SET_NULL |
| **RecommendationEvent** | user | User | ManyToOne | SET_NULL |
| **RecommendationEvent** | product | Product | ManyToOne | CASCADE |
| **UserInteraction** | user | User | ManyToOne | CASCADE |
| **UserInteraction** | product | Product | ManyToOne | CASCADE |
| **UserInteraction** | target_product | Product | ManyToOne | CASCADE |

---

## Table Count Summary

| App | Tables | Count |
|-----|--------|-------|
| **accounts** | users | 1 |
| **products** | categories, tags, products, product_images, reviews | 5 |
| **cart** | carts, cart_items | 2 |
| **orders** | orders, order_items | 2 |
| **recommendations** | recommendation_events, user_interactions | 2 |
| **analytics** | algorithm_metrics, comparison_reports | 2 |
| **TOTAL** | | **14 tables** |

---

## Key Design Notes

### 1. **User Model**
- Uses Django's `AbstractUser` with email as `USERNAME_FIELD`
- Stores address information directly on user model

### 2. **Category Hierarchy**
- Self-referential ForeignKey allows unlimited category depth
- `parent` field points to another Category

### 3. **Product Catalog**
- Products belong to one Category (FK)
- Products can have multiple Tags (M2M)
- Multiple images via ProductImage gallery
- Tracks ratings, views, and purchases counts

### 4. **Shopping Cart**
- Supports both authenticated users (OneToOne) and anonymous sessions
- Session-based carts for guest users

### 5. **Order Management**
- Order and OrderItem pattern (header-line items)
- Snapshots product name/SKU at time of purchase
- Tracks order status and payment status separately

### 6. **Recommendation System**
- Tracks recommendation events per algorithm
- UserInteraction model captures various engagement types
- Supports A/B testing multiple recommendation algorithms

### 7. **Analytics**
- AlgorithmMetrics tracks daily performance per algorithm
- ComparisonReports stores aggregated comparison data in JSON fields

---

## Indexes & Constraints

### Unique Constraints
- `User.email`
- `Category.slug`
- `Product.slug`, `Product.sku`
- `Tag.name`, `Tag.slug`
- `Order.order_number`
- `Review.product + Review.user` (unique_together)
- `CartItem.cart + CartItem.product` (unique_together)
- `AlgorithmMetrics.algorithm + AlgorithmMetrics.date` (unique_together)

### Indexes
- `Product.slug`, `Product.category`, `Product.is_available + Product.is_active`
- `RecommendationEvent.algorithm + RecommendationEvent.event_type`
- `RecommendationEvent.algorithm + RecommendationEvent.created_at`
- `UserInteraction.user + UserInteraction.interaction_type`
- `UserInteraction.product + UserInteraction.interaction_type`

---

## Generated on
**Date:** Monday, April 6, 2026
**Project:** E-commerce Alkabry
**Django Apps:** 6 apps (accounts, products, cart, orders, recommendations, analytics)
