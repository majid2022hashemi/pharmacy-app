--
-- PostgreSQL database dump
--

\restrict VCOVQeoLE2wfmugvuE0JruVry4zFjNe0jKLD2IQfGnNrbzWBjAonQJ2dv8Q2HlO

-- Dumped from database version 18.1 (Ubuntu 18.1-1.pgdg24.04+2)
-- Dumped by pg_dump version 18.1 (Ubuntu 18.1-1.pgdg24.04+2)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: auto_submit_to_insurance(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.auto_submit_to_insurance() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    IF NEW.is_insurance_approved = true THEN
        INSERT INTO insurance_transactions (
            invoice_id, insurance_id, requested_amount, status
        )
        SELECT 
            NEW.id, 
            c.insurance_id,
            NEW.insurance_discount,
            'pending'
        FROM customers c
        WHERE c.id = NEW.customer_id;
    END IF;
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.auto_submit_to_insurance() OWNER TO majid;

--
-- Name: calculate_insurance_discount(integer, numeric); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.calculate_insurance_discount(p_insurance_id integer, p_total_amount numeric) RETURNS numeric
    LANGUAGE plpgsql
    AS $$
DECLARE
    v_coverage_percent DECIMAL;
BEGIN
    SELECT discount_percent INTO v_coverage_percent
    FROM insurances WHERE id = p_insurance_id;
    
    IF v_coverage_percent IS NULL THEN
        RETURN 0;
    END IF;
    
    RETURN p_total_amount * (v_coverage_percent / 100);
END;
$$;


ALTER FUNCTION public.calculate_insurance_discount(p_insurance_id integer, p_total_amount numeric) OWNER TO majid;

--
-- Name: check_stock_before_sale(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.check_stock_before_sale() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
    v_current_stock INTEGER;
BEGIN
    SELECT quantity INTO v_current_stock
    FROM inventory 
    WHERE id = NEW.inventory_id;
    
    IF v_current_stock < NEW.quantity THEN
        RAISE EXCEPTION 'mojodi feli kafi nist!: %', v_current_stock;
    END IF;
    
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.check_stock_before_sale() OWNER TO majid;

--
-- Name: get_database_summary(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.get_database_summary() RETURNS TABLE(table_name character varying, row_count bigint)
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN QUERY
    SELECT relname::VARCHAR, n_live_tup::BIGINT
    FROM pg_stat_user_tables
    ORDER BY relname;
END;
$$;


ALTER FUNCTION public.get_database_summary() OWNER TO majid;

--
-- Name: log_stock_adjustment(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.log_stock_adjustment() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    INSERT INTO stock_adjustments (
        medicine_id, 
        batch_number, 
        adjustment_type, 
        quantity, 
        reason, 
        adjusted_by
    )
    VALUES (
        NEW.medicine_id,
        NEW.batch_number,
        'correction',
        NEW.quantity - OLD.quantity,
        'تصحیح خودکار موجودی',
        NULL
    );
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.log_stock_adjustment() OWNER TO majid;

--
-- Name: update_stock_on_sale(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.update_stock_on_sale() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    UPDATE inventory 
    SET quantity = quantity - NEW.quantity
    WHERE id = NEW.inventory_id;
    
    UPDATE medicines
    SET current_stock = (
        SELECT COALESCE(SUM(quantity), 0)
        FROM inventory 
        WHERE medicine_id = (SELECT medicine_id FROM inventory WHERE id = NEW.inventory_id)
    )
    WHERE id = (SELECT medicine_id FROM inventory WHERE id = NEW.inventory_id);
    
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.update_stock_on_sale() OWNER TO majid;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: backups; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.backups (
    id integer NOT NULL,
    backup_file_name character varying(200) NOT NULL,
    backup_path text NOT NULL,
    backup_size bigint,
    backup_type character varying(20),
    backup_date timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    created_by integer,
    checksum character varying(64),
    restore_status character varying(20) DEFAULT 'not_restored'::character varying
);


ALTER TABLE public.backups OWNER TO majid;

--
-- Name: backups_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.backups_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.backups_id_seq OWNER TO majid;

--
-- Name: backups_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.backups_id_seq OWNED BY public.backups.id;


--
-- Name: categories; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.categories (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    parent_id integer,
    description text
);


ALTER TABLE public.categories OWNER TO majid;

--
-- Name: categories_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.categories_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.categories_id_seq OWNER TO majid;

--
-- Name: categories_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.categories_id_seq OWNED BY public.categories.id;


--
-- Name: companies; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.companies (
    id integer NOT NULL,
    name character varying(200) NOT NULL,
    code character varying(20),
    phone character varying(20),
    email character varying(100),
    address text
);


ALTER TABLE public.companies OWNER TO majid;

--
-- Name: companies_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.companies_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.companies_id_seq OWNER TO majid;

--
-- Name: companies_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.companies_id_seq OWNED BY public.companies.id;


--
-- Name: customers; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.customers (
    id integer NOT NULL,
    national_code character varying(10),
    first_name character varying(100) NOT NULL,
    last_name character varying(100) NOT NULL,
    phone character varying(15),
    mobile character varying(15),
    address text,
    insurance_id integer,
    insurance_code character varying(50),
    birth_date date,
    gender character(1),
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT customers_gender_check CHECK ((gender = ANY (ARRAY['M'::bpchar, 'F'::bpchar])))
);


ALTER TABLE public.customers OWNER TO majid;

--
-- Name: customers_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.customers_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.customers_id_seq OWNER TO majid;

--
-- Name: customers_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.customers_id_seq OWNED BY public.customers.id;


--
-- Name: invoices; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.invoices (
    id integer NOT NULL,
    invoice_number character varying(50) NOT NULL,
    customer_id integer,
    pharmacist_id integer,
    invoice_date timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    total_amount numeric(12,2),
    discount_amount numeric(12,2) DEFAULT 0,
    insurance_discount numeric(12,2) DEFAULT 0,
    final_amount numeric(12,2),
    payment_method character varying(20),
    status character varying(20) DEFAULT 'completed'::character varying,
    prescription_number character varying(50),
    prescription_id integer,
    insurance_approval_code character varying(50),
    is_insurance_approved boolean DEFAULT false,
    CONSTRAINT invoices_payment_method_check CHECK (((payment_method)::text = ANY ((ARRAY['cash'::character varying, 'card'::character varying, 'insurance'::character varying, 'credit'::character varying])::text[])))
);


ALTER TABLE public.invoices OWNER TO majid;

--
-- Name: daily_sales_stats; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.daily_sales_stats AS
 SELECT date(invoice_date) AS sale_date,
    count(*) AS invoice_count,
    count(DISTINCT customer_id) AS unique_customers,
    COALESCE(sum(final_amount), (0)::numeric) AS total_sales,
    COALESCE(avg(final_amount), (0)::numeric) AS avg_sale,
    COALESCE(sum(
        CASE
            WHEN ((payment_method)::text = 'cash'::text) THEN final_amount
            ELSE (0)::numeric
        END), (0)::numeric) AS cash_sales,
    COALESCE(sum(
        CASE
            WHEN ((payment_method)::text = 'card'::text) THEN final_amount
            ELSE (0)::numeric
        END), (0)::numeric) AS card_sales,
    COALESCE(sum(
        CASE
            WHEN ((payment_method)::text = 'insurance'::text) THEN final_amount
            ELSE (0)::numeric
        END), (0)::numeric) AS insurance_sales
   FROM public.invoices
  WHERE ((status)::text = 'completed'::text)
  GROUP BY (date(invoice_date))
  ORDER BY (date(invoice_date)) DESC;


ALTER VIEW public.daily_sales_stats OWNER TO majid;

--
-- Name: electronic_prescriptions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.electronic_prescriptions (
    id integer NOT NULL,
    prescription_number character varying(50) NOT NULL,
    doctor_national_code character varying(10) NOT NULL,
    doctor_name character varying(200),
    doctor_license character varying(50),
    patient_national_code character varying(10) NOT NULL,
    patient_name character varying(200),
    issue_date timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    expiry_date date NOT NULL,
    status character varying(20) DEFAULT 'pending'::character varying,
    qr_code text,
    digital_signature text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.electronic_prescriptions OWNER TO majid;

--
-- Name: electronic_prescriptions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.electronic_prescriptions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.electronic_prescriptions_id_seq OWNER TO majid;

--
-- Name: electronic_prescriptions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.electronic_prescriptions_id_seq OWNED BY public.electronic_prescriptions.id;


--
-- Name: inventory; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.inventory (
    id integer NOT NULL,
    medicine_id integer,
    batch_number character varying(50) NOT NULL,
    expiry_date date NOT NULL,
    quantity integer NOT NULL,
    purchase_price numeric(12,2),
    sell_price numeric(12,2),
    received_date date DEFAULT CURRENT_DATE
);


ALTER TABLE public.inventory OWNER TO majid;

--
-- Name: medicines; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.medicines (
    id integer NOT NULL,
    code character varying(20) NOT NULL,
    name character varying(200) NOT NULL,
    generic_name character varying(200),
    brand_name character varying(200),
    category_id integer,
    company_id integer,
    dosage_form character varying(50),
    strength character varying(50),
    package_size character varying(50),
    is_prescription boolean DEFAULT true,
    needs_refrigeration boolean DEFAULT false,
    max_stock_level integer,
    min_stock_level integer,
    current_stock integer DEFAULT 0,
    unit_price numeric(12,2),
    sale_price numeric(12,2),
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.medicines OWNER TO majid;

--
-- Name: expiring_medicines; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.expiring_medicines AS
 SELECT m.code AS medicine_code,
    m.name AS medicine_name,
    i.batch_number,
    i.expiry_date,
    i.quantity,
    (i.expiry_date - CURRENT_DATE) AS days_to_expiry,
        CASE
            WHEN ((i.expiry_date - CURRENT_DATE) <= 30) THEN 'besyar fori '::text
            WHEN ((i.expiry_date - CURRENT_DATE) <= 60) THEN 'fori'::text
            ELSE 'عادی'::text
        END AS priority
   FROM (public.inventory i
     JOIN public.medicines m ON ((i.medicine_id = m.id)))
  WHERE ((i.expiry_date <= (CURRENT_DATE + '90 days'::interval)) AND (i.quantity > 0))
  ORDER BY i.expiry_date;


ALTER VIEW public.expiring_medicines OWNER TO majid;

--
-- Name: insurance_members; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.insurance_members (
    id integer NOT NULL,
    insurance_id integer,
    national_code character varying(10) NOT NULL,
    member_code character varying(50) NOT NULL,
    coverage_percent numeric(5,2) DEFAULT 70,
    valid_from date,
    valid_until date,
    is_active boolean DEFAULT true
);


ALTER TABLE public.insurance_members OWNER TO majid;

--
-- Name: insurance_members_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.insurance_members_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.insurance_members_id_seq OWNER TO majid;

--
-- Name: insurance_members_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.insurance_members_id_seq OWNED BY public.insurance_members.id;


--
-- Name: insurance_transactions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.insurance_transactions (
    id integer NOT NULL,
    invoice_id integer,
    insurance_id integer,
    request_date timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    approval_date timestamp without time zone,
    approval_code character varying(50),
    requested_amount numeric(12,2),
    approved_amount numeric(12,2),
    status character varying(20) DEFAULT 'pending'::character varying,
    rejection_reason text,
    payment_date timestamp without time zone,
    transaction_id character varying(100)
);


ALTER TABLE public.insurance_transactions OWNER TO majid;

--
-- Name: insurance_transactions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.insurance_transactions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.insurance_transactions_id_seq OWNER TO majid;

--
-- Name: insurance_transactions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.insurance_transactions_id_seq OWNED BY public.insurance_transactions.id;


--
-- Name: insurances; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.insurances (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    discount_percent numeric(5,2) DEFAULT 0,
    coverage_details text
);


ALTER TABLE public.insurances OWNER TO majid;

--
-- Name: insurances_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.insurances_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.insurances_id_seq OWNER TO majid;

--
-- Name: insurances_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.insurances_id_seq OWNED BY public.insurances.id;


--
-- Name: inventory_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.inventory_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.inventory_id_seq OWNER TO majid;

--
-- Name: inventory_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.inventory_id_seq OWNED BY public.inventory.id;


--
-- Name: invoice_items; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.invoice_items (
    id integer NOT NULL,
    invoice_id integer,
    inventory_id integer,
    medicine_name_at_sale character varying(200),
    quantity integer NOT NULL,
    unit_price numeric(12,2),
    discount_percent numeric(5,2) DEFAULT 0,
    total_price numeric(12,2)
);


ALTER TABLE public.invoice_items OWNER TO majid;

--
-- Name: invoice_items_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.invoice_items_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.invoice_items_id_seq OWNER TO majid;

--
-- Name: invoice_items_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.invoice_items_id_seq OWNED BY public.invoice_items.id;


--
-- Name: invoices_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.invoices_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.invoices_id_seq OWNER TO majid;

--
-- Name: invoices_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.invoices_id_seq OWNED BY public.invoices.id;


--
-- Name: low_stock_medicines; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.low_stock_medicines AS
 SELECT code,
    name,
    current_stock,
    min_stock_level,
    (min_stock_level - current_stock) AS shortage,
        CASE
            WHEN (current_stock = 0) THEN ' etmam mojodi'::text
            WHEN (current_stock <= (min_stock_level / 2)) THEN 'bohrani'::text
            ELSE 'هشدار'::text
        END AS severity
   FROM public.medicines
  WHERE (current_stock <= min_stock_level)
  ORDER BY current_stock;


ALTER VIEW public.low_stock_medicines OWNER TO majid;

--
-- Name: medicines_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.medicines_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.medicines_id_seq OWNER TO majid;

--
-- Name: medicines_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.medicines_id_seq OWNED BY public.medicines.id;


--
-- Name: prescription_items; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.prescription_items (
    id integer NOT NULL,
    prescription_id integer,
    medicine_code character varying(20),
    medicine_name character varying(200),
    dosage character varying(100),
    duration integer,
    quantity integer NOT NULL,
    instructions text,
    is_substituted boolean DEFAULT false,
    substituted_medicine_code character varying(20)
);


ALTER TABLE public.prescription_items OWNER TO majid;

--
-- Name: prescription_items_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.prescription_items_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.prescription_items_id_seq OWNER TO majid;

--
-- Name: prescription_items_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.prescription_items_id_seq OWNED BY public.prescription_items.id;


--
-- Name: purchase_items; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.purchase_items (
    id integer NOT NULL,
    purchase_id integer,
    medicine_id integer,
    batch_number character varying(50),
    quantity integer,
    purchase_price numeric(12,2),
    expiry_date date
);


ALTER TABLE public.purchase_items OWNER TO majid;

--
-- Name: purchase_items_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.purchase_items_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.purchase_items_id_seq OWNER TO majid;

--
-- Name: purchase_items_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.purchase_items_id_seq OWNED BY public.purchase_items.id;


--
-- Name: purchases; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.purchases (
    id integer NOT NULL,
    purchase_number character varying(50) NOT NULL,
    company_id integer,
    purchase_date date DEFAULT CURRENT_DATE,
    total_amount numeric(12,2),
    invoice_number character varying(50),
    paid_amount numeric(12,2),
    remaining_amount numeric(12,2),
    status character varying(20) DEFAULT 'pending'::character varying
);


ALTER TABLE public.purchases OWNER TO majid;

--
-- Name: purchases_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.purchases_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.purchases_id_seq OWNER TO majid;

--
-- Name: purchases_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.purchases_id_seq OWNED BY public.purchases.id;


--
-- Name: saved_reports; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.saved_reports (
    id integer NOT NULL,
    report_name character varying(200) NOT NULL,
    report_type character varying(50),
    report_query text,
    report_data jsonb,
    filters_applied jsonb,
    created_by integer,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.saved_reports OWNER TO majid;

--
-- Name: saved_reports_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.saved_reports_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.saved_reports_id_seq OWNER TO majid;

--
-- Name: saved_reports_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.saved_reports_id_seq OWNED BY public.saved_reports.id;


--
-- Name: stock_adjustments; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.stock_adjustments (
    id integer NOT NULL,
    medicine_id integer,
    batch_number character varying(50),
    adjustment_type character varying(20),
    quantity integer,
    reason text,
    adjusted_by integer,
    adjustment_date timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT stock_adjustments_adjustment_type_check CHECK (((adjustment_type)::text = ANY ((ARRAY['damage'::character varying, 'expired'::character varying, 'loss'::character varying, 'correction'::character varying])::text[])))
);


ALTER TABLE public.stock_adjustments OWNER TO majid;

--
-- Name: stock_adjustments_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.stock_adjustments_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.stock_adjustments_id_seq OWNER TO majid;

--
-- Name: stock_adjustments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.stock_adjustments_id_seq OWNED BY public.stock_adjustments.id;


--
-- Name: top_selling_medicines; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.top_selling_medicines AS
 SELECT m.code,
    m.name,
    count(*) AS sale_count,
    sum(ii.quantity) AS total_quantity,
    sum(ii.total_price) AS total_revenue
   FROM ((public.invoice_items ii
     JOIN public.invoices i ON ((ii.invoice_id = i.id)))
     JOIN public.medicines m ON (((ii.medicine_name_at_sale)::text = (m.name)::text)))
  WHERE ((i.status)::text = 'completed'::text)
  GROUP BY m.code, m.name
  ORDER BY (sum(ii.quantity)) DESC
 LIMIT 10;


ALTER VIEW public.top_selling_medicines OWNER TO majid;

--
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    id integer NOT NULL,
    username character varying(50) NOT NULL,
    password_hash character varying(255) NOT NULL,
    full_name character varying(100),
    role character varying(20),
    phone character varying(15),
    email character varying(100),
    is_active boolean DEFAULT true,
    last_login timestamp without time zone,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT users_role_check CHECK (((role)::text = ANY ((ARRAY['admin'::character varying, 'pharmacist'::character varying, 'cashier'::character varying, 'manager'::character varying])::text[])))
);


ALTER TABLE public.users OWNER TO majid;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_id_seq OWNER TO majid;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: backups id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.backups ALTER COLUMN id SET DEFAULT nextval('public.backups_id_seq'::regclass);


--
-- Name: categories id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.categories ALTER COLUMN id SET DEFAULT nextval('public.categories_id_seq'::regclass);


--
-- Name: companies id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.companies ALTER COLUMN id SET DEFAULT nextval('public.companies_id_seq'::regclass);


--
-- Name: customers id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.customers ALTER COLUMN id SET DEFAULT nextval('public.customers_id_seq'::regclass);


--
-- Name: electronic_prescriptions id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.electronic_prescriptions ALTER COLUMN id SET DEFAULT nextval('public.electronic_prescriptions_id_seq'::regclass);


--
-- Name: insurance_members id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.insurance_members ALTER COLUMN id SET DEFAULT nextval('public.insurance_members_id_seq'::regclass);


--
-- Name: insurance_transactions id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.insurance_transactions ALTER COLUMN id SET DEFAULT nextval('public.insurance_transactions_id_seq'::regclass);


--
-- Name: insurances id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.insurances ALTER COLUMN id SET DEFAULT nextval('public.insurances_id_seq'::regclass);


--
-- Name: inventory id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.inventory ALTER COLUMN id SET DEFAULT nextval('public.inventory_id_seq'::regclass);


--
-- Name: invoice_items id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.invoice_items ALTER COLUMN id SET DEFAULT nextval('public.invoice_items_id_seq'::regclass);


--
-- Name: invoices id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.invoices ALTER COLUMN id SET DEFAULT nextval('public.invoices_id_seq'::regclass);


--
-- Name: medicines id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.medicines ALTER COLUMN id SET DEFAULT nextval('public.medicines_id_seq'::regclass);


--
-- Name: prescription_items id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.prescription_items ALTER COLUMN id SET DEFAULT nextval('public.prescription_items_id_seq'::regclass);


--
-- Name: purchase_items id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.purchase_items ALTER COLUMN id SET DEFAULT nextval('public.purchase_items_id_seq'::regclass);


--
-- Name: purchases id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.purchases ALTER COLUMN id SET DEFAULT nextval('public.purchases_id_seq'::regclass);


--
-- Name: saved_reports id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.saved_reports ALTER COLUMN id SET DEFAULT nextval('public.saved_reports_id_seq'::regclass);


--
-- Name: stock_adjustments id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.stock_adjustments ALTER COLUMN id SET DEFAULT nextval('public.stock_adjustments_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Data for Name: backups; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.backups (id, backup_file_name, backup_path, backup_size, backup_type, backup_date, created_by, checksum, restore_status) FROM stdin;
1	pharmacy_backup_20240301_020000.dump	/backups/pharmacy/	125440000	full	2024-03-01 02:00:00	13	5d41402abc4b2a76b9719d911017c592	not_restored
2	pharmacy_backup_20240308_020000.dump	/backups/pharmacy/	128756000	full	2024-03-08 02:00:00	13	7d793037a0760186574b0282f2f435e7	not_restored
3	pharmacy_backup_20240315_020000.dump	/backups/pharmacy/	132890000	full	2024-03-15 02:00:00	13	e4d909c290d0fb1ca068ffaddf22cbd0	restored
4	pharmacy_backup_20240322_020000.dump	/backups/pharmacy/	135678000	full	2024-03-22 02:00:00	16	a9f3f6f8e5c2f4b9e8d4a1c3b5e6f7a8	not_restored
5	pharmacy_backup_20240329_020000.dump	/backups/pharmacy/	138945000	full	2024-03-29 02:00:00	13	8d5e9f1c2a3b4d5e6f7a8b9c0d1e2f3a	not_restored
6	pharmacy_schema_backup_20240310.dump	/backups/pharmacy/schemas/	25600000	schema	2024-03-10 03:00:00	14	b2c4d6f8h0j2l4n6p8r0t2v4x6z8b0d	not_restored
7	pharmacy_data_backup_20240315.dump	/backups/pharmacy/data/	102400000	data	2024-03-15 04:00:00	17	3c5e7g9i1k3m5o7q9s1u3w5y7a9c1e3	not_restored
8	pharmacy_backup_20240401_020000.dump	/backups/pharmacy/	142567000	full	2024-04-01 02:00:00	13	f7d6c8e9a0b1c2d3e4f5a6b7c8d9e0f1	not_restored
9	pharmacy_inventory_backup_20240325.dump	/backups/pharmacy/inventory/	45890000	partial	2024-03-25 05:00:00	15	a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6	not_restored
10	pharmacy_transactions_backup_20240330.dump	/backups/pharmacy/transactions/	67234000	partial	2024-03-30 06:00:00	14	p6o5n4m3l2k1j0i9h8g7f6e5d4c3b2a1	restored
\.


--
-- Data for Name: categories; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.categories (id, name, parent_id, description) FROM stdin;
1	Antibiotics	\N	Medicines that fight bacterial infections
2	Pain Relief	\N	Medications for pain management
3	Vitamins	\N	Dietary supplements and vitamins
4	Cardiovascular	\N	Heart and blood pressure medications
5	Antidiabetic	\N	Diabetes medications
6	Cold & Flu	\N	Medicines for cold and influenza
7	Antiallergic	\N	Allergy medications
8	Antidepressants	\N	Mental health medications
9	Topical	\N	Creams, ointments, and external use
10	Pediatric	\N	Children specific medications
\.


--
-- Data for Name: companies; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.companies (id, name, code, phone, email, address) FROM stdin;
1	Razak Laboratories	RAZ001	021-12345678	info@razak.com	Tehran, Iran
2	Sobhan Darou	SOB002	021-87654321	info@sobhandarou.com	Tehran, Iran
3	Abidi Pharmaceutical	ABI003	021-23456789	contact@abidi.com	Tehran, Iran
4	Novartis	NOV004	021-34567890	info@novartis.com	Basel, Switzerland
5	Pfizer	PFZ005	021-45678901	info@pfizer.com	New York, USA
6	Sanofi	SAN006	021-56789012	info@sanofi.com	Paris, France
7	Loghman Pharmaceuticals	LOG007	021-67890123	info@loghman.com	Tehran, Iran
8	Hakim Pharmaceutical	HAK008	021-78901234	info@hakim.com	Tehran, Iran
9	Glakso	GLA009	021-89012345	info@glakso.com	London, UK
10	Bayer	BAY010	021-90123456	info@bayer.com	Leverkusen, Germany
\.


--
-- Data for Name: customers; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.customers (id, national_code, first_name, last_name, phone, mobile, address, insurance_id, insurance_code, birth_date, gender, created_at) FROM stdin;
1	1234567890	Ali	Rezaei	021-12345678	09121112222	Tehran, Valiasr St	1	INS001	1985-03-15	M	2026-05-05 03:09:56.9316
2	2345678901	Sara	Mohammadi	021-23456789	09123334444	Tehran, Pasdaran St	2	INS002	1990-07-22	F	2026-05-05 03:09:56.9316
3	3456789012	Mohammad	Karimi	021-34567890	09125556666	Tehran, Vanak Sq	1	INS003	1978-12-10	M	2026-05-05 03:09:56.9316
4	4567890123	Fatemeh	Hosseini	021-45678901	09127778888	Tehran, Niavaran St	3	INS004	1995-04-05	F	2026-05-05 03:09:56.9316
5	5678901234	Reza	Ahmadi	021-56789012	09129990000	Karaj, Azadi St	\N	\N	1982-09-18	M	2026-05-05 03:09:56.9316
6	6789012345	Zahra	Ebrahimi	021-67890123	09101111111	Tehran, Sattarkhan St	4	INS005	1988-11-25	F	2026-05-05 03:09:56.9316
7	7890123456	Hossein	Moradi	021-78901234	09102223333	Tehran, Molavi St	2	INS006	1975-06-30	M	2026-05-05 03:09:56.9316
8	8901234567	Neda	Jafari	021-89012345	09103334444	Tehran, Ekbatan	5	INS007	1992-08-12	F	2026-05-05 03:09:56.9316
9	9012345678	Majid	Gholami	021-90123456	09104445555	Tehran, Shariati St	1	INS008	1980-01-20	M	2026-05-05 03:09:56.9316
10	0123456789	Leila	Ranjbar	021-01234567	09105556666	Tehran, Tajrish Sq	6	INS009	1993-05-03	F	2026-05-05 03:09:56.9316
\.


--
-- Data for Name: electronic_prescriptions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.electronic_prescriptions (id, prescription_number, doctor_national_code, doctor_name, doctor_license, patient_national_code, patient_name, issue_date, expiry_date, status, qr_code, digital_signature, created_at) FROM stdin;
16	RX00124	1111111111	Dr. Mohammad Taghavi	DOC12345	1234567890	Ali Rezaei	2024-03-01 09:00:00	2024-04-01	filled	QR1234567890	\N	2026-05-05 03:11:21.63232
17	RX00125	2222222222	Dr. Saeed Hashemi	DOC12346	3456789012	Mohammad Karimi	2024-03-01 13:00:00	2024-04-01	filled	QR1234567891	\N	2026-05-05 03:11:21.63232
18	RX00126	3333333333	Dr. Neda Ahmadi	DOC12347	6789012345	Zahra Ebrahimi	2024-03-02 10:00:00	2024-04-02	filled	QR1234567892	\N	2026-05-05 03:11:21.63232
19	RX00127	1111111111	Dr. Mohammad Taghavi	DOC12345	7890123456	Hossein Moradi	2024-03-03 09:30:00	2024-04-03	filled	QR1234567893	\N	2026-05-05 03:11:21.63232
20	RX00128	4444444444	Dr. Reza Pourreza	DOC12348	0123456789	Leila Ranjbar	2024-03-04 10:00:00	2024-04-04	filled	QR1234567894	\N	2026-05-05 03:11:21.63232
\.


--
-- Data for Name: insurance_members; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.insurance_members (id, insurance_id, national_code, member_code, coverage_percent, valid_from, valid_until, is_active) FROM stdin;
\.


--
-- Data for Name: insurance_transactions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.insurance_transactions (id, invoice_id, insurance_id, request_date, approval_date, approval_code, requested_amount, approved_amount, status, rejection_reason, payment_date, transaction_id) FROM stdin;
1	21	1	2026-05-05 04:03:35.884613	\N	\N	87500.00	\N	pending	\N	\N	\N
2	23	1	2026-05-05 04:03:35.884613	\N	\N	175000.00	\N	pending	\N	\N	\N
3	26	4	2026-05-05 04:03:35.884613	\N	\N	64400.00	\N	pending	\N	\N	\N
4	27	2	2026-05-05 04:03:35.884613	\N	\N	105000.00	\N	pending	\N	\N	\N
5	30	6	2026-05-05 04:03:35.884613	\N	\N	147000.00	\N	pending	\N	\N	\N
\.


--
-- Data for Name: insurances; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.insurances (id, name, discount_percent, coverage_details) FROM stdin;
1	Iran Health Insurance	70.00	Coverage for outpatient and inpatient services
2	Social Security Organization	80.00	Full coverage for insured individuals
3	Armed Forces Insurance	75.00	Special coverage for military personnel
4	Imam Khomeini Relief Foundation	90.00	Coverage for low-income families
5	Private Insurance Alborz	60.00	Supplementary health insurance
6	Private Insurance Asia	65.00	Comprehensive health coverage with dental
\.


--
-- Data for Name: inventory; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.inventory (id, medicine_id, batch_number, expiry_date, quantity, purchase_price, sell_price, received_date) FROM stdin;
24	24	BATCH009	2025-06-30	118	16000.00	25000.00	2024-01-05
23	23	BATCH008	2025-11-30	939	1500.00	3500.00	2024-02-10
16	16	BATCH001	2025-12-31	346	7500.00	12000.00	2024-01-15
18	18	BATCH003	2025-11-30	447	2200.00	4500.00	2024-02-01
25	25	BATCH010	2025-10-31	417	2800.00	5000.00	2024-01-28
26	26	BATCH011	2025-12-31	84	75000.00	120000.00	2024-02-15
27	27	BATCH012	2025-05-31	159	40000.00	65000.00	2024-01-22
17	17	BATCH002	2025-10-31	744	3000.00	5500.00	2024-01-20
19	19	BATCH004	2025-08-31	192	13000.00	22000.00	2024-01-10
20	20	BATCH005	2025-12-31	372	4800.00	8500.00	2024-01-25
29	29	BATCH014	2025-04-30	173	8200.00	14000.00	2024-01-12
28	28	BATCH013	2025-09-30	89	10000.00	18000.00	2024-02-08
22	22	BATCH007	2025-07-31	275	6000.00	10500.00	2024-01-18
30	30	BATCH015	2025-08-31	591	3500.00	6500.00	2024-01-30
21	21	BATCH006	2025-09-30	642	2000.00	4000.00	2024-02-05
\.


--
-- Data for Name: invoice_items; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.invoice_items (id, invoice_id, inventory_id, medicine_name_at_sale, quantity, unit_price, discount_percent, total_price) FROM stdin;
1	21	16	Amoxicillin 500mg	2	12000.00	0.00	24000.00
2	21	18	Cetirizine 10mg	1	4500.00	0.00	4500.00
3	21	23	Paracetamol 500mg	3	3500.00	0.00	10500.00
4	21	30	Multivitamin	4	6500.00	0.00	26000.00
5	22	23	Paracetamol 500mg	5	3500.00	0.00	17500.00
6	22	21	Vitamin C	2	4000.00	0.00	8000.00
7	23	19	Atorvastatin 20mg	3	22000.00	0.00	66000.00
8	23	22	Omeprazole 20mg	2	10500.00	0.00	21000.00
9	23	24	Azithromycin 250mg	2	25000.00	0.00	50000.00
10	24	23	Paracetamol 500mg	3	3500.00	0.00	10500.00
11	24	21	Vitamin C	2	4000.00	0.00	8000.00
12	25	20	Metformin 500mg	4	8500.00	5.00	32300.00
13	25	16	Amoxicillin 500mg	2	12000.00	10.00	21600.00
14	26	18	Cetirizine 10mg	2	4500.00	0.00	9000.00
15	26	25	Loratadine 10mg	3	5000.00	0.00	15000.00
16	27	26	Insulin	1	120000.00	0.00	120000.00
17	27	27	Salbutamol Inhaler	1	65000.00	0.00	65000.00
18	28	17	Ibuprofen 400mg	6	5500.00	0.00	33000.00
19	28	19	Atorvastatin 20mg	5	22000.00	0.00	110000.00
20	28	20	Metformin 500mg	4	8500.00	0.00	34000.00
21	29	29	Ciprofloxacin 500mg	2	14000.00	0.00	28000.00
22	29	28	Diazepam 5mg	1	18000.00	0.00	18000.00
23	30	22	Omeprazole 20mg	3	10500.00	0.00	31500.00
24	30	30	Multivitamin	5	6500.00	0.00	32500.00
25	30	21	Vitamin C	4	4000.00	0.00	16000.00
\.


--
-- Data for Name: invoices; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.invoices (id, invoice_number, customer_id, pharmacist_id, invoice_date, total_amount, discount_amount, insurance_discount, final_amount, payment_method, status, prescription_number, prescription_id, insurance_approval_code, is_insurance_approved) FROM stdin;
21	INV-2024-001	1	14	2024-03-01 10:30:00	125000.00	0.00	87500.00	37500.00	insurance	completed	RX00124	16	APP001	t
22	INV-2024-002	2	14	2024-03-01 11:15:00	42500.00	5000.00	0.00	37500.00	cash	completed	\N	\N	\N	f
23	INV-2024-003	3	17	2024-03-01 14:45:00	250000.00	0.00	175000.00	75000.00	insurance	completed	RX00125	17	APP002	t
24	INV-2024-004	4	14	2024-03-02 09:30:00	52000.00	2000.00	0.00	50000.00	card	completed	\N	\N	\N	f
25	INV-2024-005	5	17	2024-03-02 12:00:00	185000.00	15000.00	0.00	170000.00	cash	completed	\N	\N	\N	f
26	INV-2024-006	6	14	2024-03-02 16:20:00	92000.00	0.00	64400.00	27600.00	insurance	completed	RX00126	18	APP003	t
27	INV-2024-007	7	17	2024-03-03 10:00:00	150000.00	0.00	105000.00	45000.00	insurance	completed	RX00127	19	APP004	t
28	INV-2024-008	8	14	2024-03-03 13:30:00	348000.00	50000.00	0.00	298000.00	card	completed	\N	\N	\N	f
29	INV-2024-009	9	17	2024-03-03 15:45:00	75000.00	5000.00	0.00	70000.00	cash	completed	\N	\N	\N	f
30	INV-2024-010	10	14	2024-03-04 11:00:00	210000.00	0.00	147000.00	63000.00	insurance	completed	RX00128	20	APP005	t
\.


--
-- Data for Name: medicines; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.medicines (id, code, name, generic_name, brand_name, category_id, company_id, dosage_form, strength, package_size, is_prescription, needs_refrigeration, max_stock_level, min_stock_level, current_stock, unit_price, sale_price, created_at) FROM stdin;
24	MED009	Azithromycin	Azithromycin	Zithromax	1	9	Tablet	250mg	12 tablets	t	f	300	30	118	18000.00	25000.00	2026-05-05 02:43:13.041552
23	MED008	Paracetamol	Acetaminophen	Panadol	2	8	Tablet	500mg	24 tablets	f	f	1500	150	939	2000.00	3500.00	2026-05-05 02:43:13.041552
16	MED001	Amoxicillin	Amoxicillin	Amoxil	1	1	Capsule	500mg	20 capsules	t	f	500	50	346	8500.00	12000.00	2026-05-05 02:43:13.041552
18	MED003	Cetirizine	Cetirizine HCl	Zyrtec	3	3	Tablet	10mg	20 tablets	f	f	800	80	447	2800.00	4500.00	2026-05-05 02:43:13.041552
25	MED010	Loratadine	Loratadine	Claritin	7	10	Tablet	10mg	20 tablets	f	f	700	70	417	3200.00	5000.00	2026-05-05 02:43:13.041552
26	MED011	Insulin	Insulin Glargine	Lantus	5	4	Injection	100 IU/ml	10ml vial	t	t	200	20	84	85000.00	120000.00	2026-05-05 02:43:13.041552
27	MED012	Salbutamol	Salbutamol	Ventolin	6	5	Inhaler	100mcg	200 doses	t	f	300	30	159	45000.00	65000.00	2026-05-05 02:43:13.041552
17	MED002	Ibuprofen	Ibuprofen	Advil	2	2	Tablet	400mg	30 tablets	f	f	1000	100	744	3500.00	5500.00	2026-05-05 02:43:13.041552
19	MED004	Atorvastatin	Atorvastatin	Lipitor	4	4	Tablet	20mg	30 tablets	t	f	400	40	192	15000.00	22000.00	2026-05-05 02:43:13.041552
20	MED005	Metformin	Metformin HCl	Glucophage	5	5	Tablet	500mg	60 tablets	t	f	600	60	372	5500.00	8500.00	2026-05-05 02:43:13.041552
29	MED014	Ciprofloxacin	Ciprofloxacin	Cipro	1	2	Tablet	500mg	20 tablets	t	f	350	35	173	9500.00	14000.00	2026-05-05 02:43:13.041552
28	MED013	Diazepam	Diazepam	Valium	8	3	Tablet	5mg	30 tablets	t	f	250	25	89	12000.00	18000.00	2026-05-05 02:43:13.041552
22	MED007	Omeprazole	Omeprazole	Prilosec	7	7	Capsule	20mg	28 capsules	t	f	500	50	275	7000.00	10500.00	2026-05-05 02:43:13.041552
30	MED015	Multivitamin	Multivitamin Complex	Multibion	3	1	Tablet	Multivitamin	30 tablets	f	f	900	90	591	4000.00	6500.00	2026-05-05 02:43:13.041552
21	MED006	Vitamin C	Ascorbic Acid	Vitamin C	6	6	Tablet	500mg	50 tablets	f	f	1000	100	642	2500.00	4000.00	2026-05-05 02:43:13.041552
\.


--
-- Data for Name: prescription_items; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.prescription_items (id, prescription_id, medicine_code, medicine_name, dosage, duration, quantity, instructions, is_substituted, substituted_medicine_code) FROM stdin;
11	16	MED001	Amoxicillin	500mg twice daily	7	14	Take with food	f	\N
12	17	MED008	Paracetamol	500mg when needed	5	10	For fever and pain	f	\N
13	18	MED004	Atorvastatin	20mg daily	30	30	Take in evening	f	\N
14	19	MED007	Omeprazole	20mg daily	30	30	Before breakfast	f	\N
15	20	MED003	Cetirizine	10mg daily	30	30	At bedtime	t	MED010
\.


--
-- Data for Name: purchase_items; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.purchase_items (id, purchase_id, medicine_id, batch_number, quantity, purchase_price, expiry_date) FROM stdin;
1	1	16	BATCH001	500	7500.00	2025-12-31
2	2	17	BATCH002	800	3000.00	2025-10-31
3	3	18	BATCH003	400	2200.00	2025-11-30
4	4	19	BATCH004	250	13000.00	2025-08-31
5	5	20	BATCH005	300	4800.00	2025-12-31
\.


--
-- Data for Name: purchases; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.purchases (id, purchase_number, company_id, purchase_date, total_amount, invoice_number, paid_amount, remaining_amount, status) FROM stdin;
1	PUR-2024-001	1	2024-01-15	2560000.00	INV-SUP-001	2560000.00	0.00	completed
2	PUR-2024-002	2	2024-01-20	1850000.00	INV-SUP-002	1500000.00	350000.00	pending
3	PUR-2024-003	3	2024-02-01	972000.00	INV-SUP-003	972000.00	0.00	completed
4	PUR-2024-004	4	2024-02-10	3200000.00	INV-SUP-004	2000000.00	1200000.00	pending
5	PUR-2024-005	5	2024-02-15	1420000.00	INV-SUP-005	1420000.00	0.00	completed
\.


--
-- Data for Name: saved_reports; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.saved_reports (id, report_name, report_type, report_query, report_data, filters_applied, created_by, created_at) FROM stdin;
1	Daily Sales Report	sales	SELECT DATE(invoice_date) as sale_date, COUNT(*) as invoice_count, SUM(final_amount) as total_sales FROM invoices WHERE status = 'completed' GROUP BY DATE(invoice_date) ORDER BY DATE(invoice_date) DESC	{"total_sales": 1250000, "invoice_count": 10}	{"date_to": "2024-03-04", "date_from": "2024-03-01"}	13	2024-03-05 10:00:00
2	Expiring Medicines Report	inventory	SELECT m.code, m.name, i.batch_number, i.expiry_date, i.quantity FROM inventory i JOIN medicines m ON i.medicine_id = m.id WHERE i.expiry_date <= CURRENT_DATE + INTERVAL '90 days' ORDER BY i.expiry_date ASC	{"critical_count": 2, "expiring_count": 5}	{"priority": "high", "days_threshold": 90}	14	2024-03-05 11:30:00
3	Top Selling Medicines	sales	SELECT m.name, COUNT(ii.id) as times_sold, SUM(ii.quantity) as total_quantity, SUM(ii.total_price) as revenue FROM invoice_items ii JOIN invoices i ON ii.invoice_id = i.id JOIN medicines m ON ii.medicine_name_at_sale = m.name GROUP BY m.name ORDER BY revenue DESC LIMIT 10	{"top_revenue": 45600, "top_medicine": "Amoxicillin"}	{"limit": 10, "period": "monthly"}	15	2024-03-05 14:15:00
4	Pharmacist Performance Report	users	SELECT u.full_name, COUNT(i.id) as prescriptions_filled, SUM(i.final_amount) as total_sales FROM users u JOIN invoices i ON u.id = i.pharmacist_id WHERE u.role = 'pharmacist' AND i.status = 'completed' GROUP BY u.full_name ORDER BY total_sales DESC	{"top_pharmacist": "Dr. Ahmad Rezaei", "total_prescriptions": 8}	{"role": "pharmacist", "date_range": "2024-03-01 to 2024-03-04"}	13	2024-03-05 16:00:00
5	VIP Customers Report	customers	SELECT c.first_name, c.last_name, COUNT(i.id) as purchase_count, SUM(i.final_amount) as total_spent FROM customers c JOIN invoices i ON c.id = i.customer_id WHERE i.status = 'completed' GROUP BY c.id ORDER BY total_spent DESC LIMIT 5	{"top_customer": "Ali Rezaei", "total_customers": 10}	{"sort_by": "total_spent", "min_purchases": 1}	16	2024-03-05 17:30:00
6	Insurance Revenue Report	insurance	SELECT ins.name as insurance_name, COUNT(i.id) as invoice_count, SUM(i.insurance_discount) as total_discount, SUM(i.final_amount) as patient_payment FROM invoices i JOIN customers c ON i.customer_id = c.id JOIN insurances ins ON c.insurance_id = ins.id WHERE i.payment_method = 'insurance' AND i.status = 'completed' GROUP BY ins.name	{"total_claims": 5, "total_insurance_discount": 578900}	{"status": "approved", "insurance_type": "all"}	14	2024-03-06 09:00:00
7	Inventory Stock Report	inventory	SELECT m.code, m.name, m.current_stock, m.min_stock_level, m.max_stock_level, (m.current_stock - m.min_stock_level) as stock_status FROM medicines m ORDER BY stock_status ASC	{"out_of_stock": 0, "low_stock_items": 3}	{"include_inactive": false, "show_low_stock_only": false}	17	2024-03-06 10:30:00
8	Profit & Loss Report	financial	SELECT 'total_sales' as metric, COALESCE(SUM(final_amount), 0) as value FROM invoices WHERE status = 'completed' UNION ALL SELECT 'total_purchases', COALESCE(SUM(total_amount), 0) FROM purchases	{"total_cost": 953000, "profit_margin": 35.5, "total_revenue": 1478500}	{"period": "2024-03", "include_tax": false}	13	2024-03-06 11:45:00
9	Electronic Prescriptions Report	prescriptions	SELECT ep.status, COUNT(*) as count, AVG(EXTRACT(DAY FROM (ep.expiry_date - ep.issue_date))) as avg_validity_days FROM electronic_prescriptions ep GROUP BY ep.status	{"filled_prescriptions": 5, "expired_prescriptions": 0, "pending_prescriptions": 0}	{"status": "filled", "date_range": "last_month"}	15	2024-03-06 13:20:00
10	Payment Methods Report	payment	SELECT payment_method, COUNT(*) as usage_count, SUM(final_amount) as total_amount FROM invoices WHERE status = 'completed' GROUP BY payment_method ORDER BY total_amount DESC	{"card_percentage": 20, "cash_percentage": 30, "insurance_percentage": 50}	{"min_amount": 0, "exclude_canceled": true}	16	2024-03-06 15:00:00
\.


--
-- Data for Name: stock_adjustments; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.stock_adjustments (id, medicine_id, batch_number, adjustment_type, quantity, reason, adjusted_by, adjustment_date) FROM stdin;
1	16	BATCH001	damage	5	Damaged packaging during handling	14	2024-02-20 10:00:00
2	18	BATCH003	expired	10	Near expiry returned to supplier	17	2024-02-25 14:30:00
3	21	BATCH006	correction	20	Inventory count adjustment after physical count	14	2024-03-01 09:00:00
4	20	BATCH005	loss	8	Medication lost during internal transfer	16	2024-02-28 11:15:00
5	22	BATCH007	damage	3	Broken vials during shipment	17	2024-03-02 13:45:00
6	24	BATCH009	expired	2	Partial expiry of batch	14	2024-03-03 10:30:00
7	26	BATCH011	correction	1	System stock correction after audit	13	2024-03-04 09:00:00
8	27	BATCH012	damage	1	Damaged inhaler device	15	2024-03-05 14:20:00
9	17	BATCH002	loss	6	Unaccounted discrepancy	16	2024-03-01 16:00:00
10	19	BATCH004	correction	8	Inventory recount adjustment	14	2024-03-06 11:00:00
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.users (id, username, password_hash, full_name, role, phone, email, is_active, last_login, created_at) FROM stdin;
13	admin	hash_admin_123	System Administrator	admin	021-11111111	admin@pharmacy.com	t	2024-03-01 08:00:00	2026-05-05 02:44:03.737386
14	pharmacist1	hash_pharm_456	Dr. Ahmad Rezaei	pharmacist	021-22222222	pharmacist@pharmacy.com	t	2024-03-01 09:30:00	2026-05-05 02:44:03.737386
15	cashier1	hash_cash_789	Maryam Karimi	cashier	021-33333333	cashier@pharmacy.com	t	2024-03-01 10:15:00	2026-05-05 02:44:03.737386
16	manager1	hash_mgr_101	Karim Mohammadi	manager	021-44444444	manager@pharmacy.com	t	2024-03-01 08:45:00	2026-05-05 02:44:03.737386
17	pharmacist2	hash_pharm_202	Dr. Sara Ebrahimi	pharmacist	021-55555555	dr.sara@pharmacy.com	t	2024-02-28 14:20:00	2026-05-05 02:44:03.737386
\.


--
-- Name: backups_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.backups_id_seq', 10, true);


--
-- Name: categories_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.categories_id_seq', 10, true);


--
-- Name: companies_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.companies_id_seq', 10, true);


--
-- Name: customers_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.customers_id_seq', 11, true);


--
-- Name: electronic_prescriptions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.electronic_prescriptions_id_seq', 20, true);


--
-- Name: insurance_members_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.insurance_members_id_seq', 1, false);


--
-- Name: insurance_transactions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.insurance_transactions_id_seq', 5, true);


--
-- Name: insurances_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.insurances_id_seq', 6, true);


--
-- Name: inventory_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.inventory_id_seq', 30, true);


--
-- Name: invoice_items_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.invoice_items_id_seq', 25, true);


--
-- Name: invoices_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.invoices_id_seq', 30, true);


--
-- Name: medicines_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.medicines_id_seq', 30, true);


--
-- Name: prescription_items_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.prescription_items_id_seq', 15, true);


--
-- Name: purchase_items_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.purchase_items_id_seq', 5, true);


--
-- Name: purchases_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.purchases_id_seq', 5, true);


--
-- Name: saved_reports_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.saved_reports_id_seq', 10, true);


--
-- Name: stock_adjustments_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.stock_adjustments_id_seq', 10, true);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.users_id_seq', 17, true);


--
-- Name: backups backups_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.backups
    ADD CONSTRAINT backups_pkey PRIMARY KEY (id);


--
-- Name: categories categories_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.categories
    ADD CONSTRAINT categories_pkey PRIMARY KEY (id);


--
-- Name: companies companies_code_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.companies
    ADD CONSTRAINT companies_code_key UNIQUE (code);


--
-- Name: companies companies_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.companies
    ADD CONSTRAINT companies_pkey PRIMARY KEY (id);


--
-- Name: customers customers_mobile_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.customers
    ADD CONSTRAINT customers_mobile_key UNIQUE (mobile);


--
-- Name: customers customers_national_code_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.customers
    ADD CONSTRAINT customers_national_code_key UNIQUE (national_code);


--
-- Name: customers customers_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.customers
    ADD CONSTRAINT customers_pkey PRIMARY KEY (id);


--
-- Name: electronic_prescriptions electronic_prescriptions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.electronic_prescriptions
    ADD CONSTRAINT electronic_prescriptions_pkey PRIMARY KEY (id);


--
-- Name: electronic_prescriptions electronic_prescriptions_prescription_number_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.electronic_prescriptions
    ADD CONSTRAINT electronic_prescriptions_prescription_number_key UNIQUE (prescription_number);


--
-- Name: insurance_members insurance_members_insurance_id_national_code_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.insurance_members
    ADD CONSTRAINT insurance_members_insurance_id_national_code_key UNIQUE (insurance_id, national_code);


--
-- Name: insurance_members insurance_members_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.insurance_members
    ADD CONSTRAINT insurance_members_pkey PRIMARY KEY (id);


--
-- Name: insurance_transactions insurance_transactions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.insurance_transactions
    ADD CONSTRAINT insurance_transactions_pkey PRIMARY KEY (id);


--
-- Name: insurances insurances_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.insurances
    ADD CONSTRAINT insurances_pkey PRIMARY KEY (id);


--
-- Name: inventory inventory_medicine_id_batch_number_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.inventory
    ADD CONSTRAINT inventory_medicine_id_batch_number_key UNIQUE (medicine_id, batch_number);


--
-- Name: inventory inventory_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.inventory
    ADD CONSTRAINT inventory_pkey PRIMARY KEY (id);


--
-- Name: invoice_items invoice_items_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.invoice_items
    ADD CONSTRAINT invoice_items_pkey PRIMARY KEY (id);


--
-- Name: invoices invoices_invoice_number_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.invoices
    ADD CONSTRAINT invoices_invoice_number_key UNIQUE (invoice_number);


--
-- Name: invoices invoices_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.invoices
    ADD CONSTRAINT invoices_pkey PRIMARY KEY (id);


--
-- Name: medicines medicines_code_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.medicines
    ADD CONSTRAINT medicines_code_key UNIQUE (code);


--
-- Name: medicines medicines_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.medicines
    ADD CONSTRAINT medicines_pkey PRIMARY KEY (id);


--
-- Name: prescription_items prescription_items_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.prescription_items
    ADD CONSTRAINT prescription_items_pkey PRIMARY KEY (id);


--
-- Name: purchase_items purchase_items_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.purchase_items
    ADD CONSTRAINT purchase_items_pkey PRIMARY KEY (id);


--
-- Name: purchases purchases_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.purchases
    ADD CONSTRAINT purchases_pkey PRIMARY KEY (id);


--
-- Name: purchases purchases_purchase_number_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.purchases
    ADD CONSTRAINT purchases_purchase_number_key UNIQUE (purchase_number);


--
-- Name: saved_reports saved_reports_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.saved_reports
    ADD CONSTRAINT saved_reports_pkey PRIMARY KEY (id);


--
-- Name: stock_adjustments stock_adjustments_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.stock_adjustments
    ADD CONSTRAINT stock_adjustments_pkey PRIMARY KEY (id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: users users_username_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_username_key UNIQUE (username);


--
-- Name: idx_customers_mobile; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_customers_mobile ON public.customers USING btree (mobile);


--
-- Name: idx_customers_national; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_customers_national ON public.customers USING btree (national_code);


--
-- Name: idx_insurance_members_national; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_insurance_members_national ON public.insurance_members USING btree (national_code);


--
-- Name: idx_insurance_transactions_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_insurance_transactions_status ON public.insurance_transactions USING btree (status);


--
-- Name: idx_inventory_expiry; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_inventory_expiry ON public.inventory USING btree (expiry_date);


--
-- Name: idx_inventory_medicine; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_inventory_medicine ON public.inventory USING btree (medicine_id);


--
-- Name: idx_invoice_items_invoice; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_invoice_items_invoice ON public.invoice_items USING btree (invoice_id);


--
-- Name: idx_invoices_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_invoices_date ON public.invoices USING btree (invoice_date);


--
-- Name: idx_invoices_insurance; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_invoices_insurance ON public.invoices USING btree (insurance_approval_code);


--
-- Name: idx_medicines_code; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_medicines_code ON public.medicines USING btree (code);


--
-- Name: idx_medicines_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_medicines_name ON public.medicines USING btree (name);


--
-- Name: idx_prescriptions_doctor; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_prescriptions_doctor ON public.electronic_prescriptions USING btree (doctor_national_code);


--
-- Name: idx_prescriptions_patient; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_prescriptions_patient ON public.electronic_prescriptions USING btree (patient_national_code);


--
-- Name: idx_prescriptions_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_prescriptions_status ON public.electronic_prescriptions USING btree (status);


--
-- Name: idx_purchases_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_purchases_date ON public.purchases USING btree (purchase_date);


--
-- Name: invoice_items trigger_check_stock; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER trigger_check_stock BEFORE INSERT ON public.invoice_items FOR EACH ROW EXECUTE FUNCTION public.check_stock_before_sale();


--
-- Name: invoices trigger_insurance_submit; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER trigger_insurance_submit AFTER INSERT ON public.invoices FOR EACH ROW EXECUTE FUNCTION public.auto_submit_to_insurance();


--
-- Name: invoice_items trigger_update_stock; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER trigger_update_stock AFTER INSERT ON public.invoice_items FOR EACH ROW EXECUTE FUNCTION public.update_stock_on_sale();


--
-- Name: backups backups_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.backups
    ADD CONSTRAINT backups_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- Name: categories categories_parent_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.categories
    ADD CONSTRAINT categories_parent_id_fkey FOREIGN KEY (parent_id) REFERENCES public.categories(id);


--
-- Name: customers customers_insurance_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.customers
    ADD CONSTRAINT customers_insurance_id_fkey FOREIGN KEY (insurance_id) REFERENCES public.insurances(id);


--
-- Name: insurance_members insurance_members_insurance_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.insurance_members
    ADD CONSTRAINT insurance_members_insurance_id_fkey FOREIGN KEY (insurance_id) REFERENCES public.insurances(id);


--
-- Name: insurance_transactions insurance_transactions_insurance_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.insurance_transactions
    ADD CONSTRAINT insurance_transactions_insurance_id_fkey FOREIGN KEY (insurance_id) REFERENCES public.insurances(id);


--
-- Name: insurance_transactions insurance_transactions_invoice_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.insurance_transactions
    ADD CONSTRAINT insurance_transactions_invoice_id_fkey FOREIGN KEY (invoice_id) REFERENCES public.invoices(id);


--
-- Name: inventory inventory_medicine_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.inventory
    ADD CONSTRAINT inventory_medicine_id_fkey FOREIGN KEY (medicine_id) REFERENCES public.medicines(id);


--
-- Name: invoice_items invoice_items_inventory_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.invoice_items
    ADD CONSTRAINT invoice_items_inventory_id_fkey FOREIGN KEY (inventory_id) REFERENCES public.inventory(id);


--
-- Name: invoice_items invoice_items_invoice_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.invoice_items
    ADD CONSTRAINT invoice_items_invoice_id_fkey FOREIGN KEY (invoice_id) REFERENCES public.invoices(id) ON DELETE CASCADE;


--
-- Name: invoices invoices_customer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.invoices
    ADD CONSTRAINT invoices_customer_id_fkey FOREIGN KEY (customer_id) REFERENCES public.customers(id);


--
-- Name: invoices invoices_pharmacist_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.invoices
    ADD CONSTRAINT invoices_pharmacist_id_fkey FOREIGN KEY (pharmacist_id) REFERENCES public.users(id);


--
-- Name: invoices invoices_prescription_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.invoices
    ADD CONSTRAINT invoices_prescription_id_fkey FOREIGN KEY (prescription_id) REFERENCES public.electronic_prescriptions(id);


--
-- Name: medicines medicines_category_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.medicines
    ADD CONSTRAINT medicines_category_id_fkey FOREIGN KEY (category_id) REFERENCES public.categories(id);


--
-- Name: medicines medicines_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.medicines
    ADD CONSTRAINT medicines_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.companies(id);


--
-- Name: prescription_items prescription_items_medicine_code_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.prescription_items
    ADD CONSTRAINT prescription_items_medicine_code_fkey FOREIGN KEY (medicine_code) REFERENCES public.medicines(code);


--
-- Name: prescription_items prescription_items_prescription_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.prescription_items
    ADD CONSTRAINT prescription_items_prescription_id_fkey FOREIGN KEY (prescription_id) REFERENCES public.electronic_prescriptions(id) ON DELETE CASCADE;


--
-- Name: purchase_items purchase_items_medicine_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.purchase_items
    ADD CONSTRAINT purchase_items_medicine_id_fkey FOREIGN KEY (medicine_id) REFERENCES public.medicines(id);


--
-- Name: purchase_items purchase_items_purchase_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.purchase_items
    ADD CONSTRAINT purchase_items_purchase_id_fkey FOREIGN KEY (purchase_id) REFERENCES public.purchases(id) ON DELETE CASCADE;


--
-- Name: purchases purchases_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.purchases
    ADD CONSTRAINT purchases_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.companies(id);


--
-- Name: saved_reports saved_reports_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.saved_reports
    ADD CONSTRAINT saved_reports_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- Name: stock_adjustments stock_adjustments_adjusted_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.stock_adjustments
    ADD CONSTRAINT stock_adjustments_adjusted_by_fkey FOREIGN KEY (adjusted_by) REFERENCES public.users(id);


--
-- Name: stock_adjustments stock_adjustments_medicine_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.stock_adjustments
    ADD CONSTRAINT stock_adjustments_medicine_id_fkey FOREIGN KEY (medicine_id) REFERENCES public.medicines(id);


--
-- PostgreSQL database dump complete
--

\unrestrict VCOVQeoLE2wfmugvuE0JruVry4zFjNe0jKLD2IQfGnNrbzWBjAonQJ2dv8Q2HlO

