# Path of file checked manually
path = "/Users/andrew.craik/Nextcloud/Renting-Andrew/Ashwood Gait/2022-23/2022-08.pdf"

num_transactions = 24
totals_sum = 222.72
amounts = [63.6, -140.16, 216.24, 144, 379.08, 846, 379.08, 84.86, 144, 846, 66, 522, 144, 142.48, 195.14, 156.17, 379.08, 277.20, 846, 66, 2800, -233.33, 37.25, 2058.48]
totals = [2.36, -5.19, 8.01, 5.33, 14.04, 2.58, 14.04, 3.14, 5.33, 2.58, 2.47, 1.59, 5.33, 5.28, 7.23, 5.78, 14.04, 10.27, 2.58, 2.44, 233.33, -233.33, 37.25, 76.24]
shares = ["1/27"] * 5 + ["1/328"] + ["1/27"]*3 + ["1/328", "1/27", "1/328"] + ["1/27"]*6 + ["1/328", "1/27", "1/12"] + ["1/1"]*2 + ["1/27"]

# Check values for tests
assert num_transactions == len(amounts)
assert num_transactions == len(totals)
assert num_transactions == len(shares)
assert round(sum(totals), 2) == round(totals_sum, 2)

# Process PDF
