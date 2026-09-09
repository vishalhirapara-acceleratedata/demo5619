-- Total sales aggregated by calendar month from the sales table.
SELECT
    date_trunc('month', order_date) AS month,
    sum(amount) AS total_sales
FROM sales
GROUP BY 1
ORDER BY 1;
