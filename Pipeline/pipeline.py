import pandas as pd
import numpy as np

# LOAD DATA (TOO SHOW IN RUNNING BAR)

print("\n" + "=" * 60)
print("LOADING DATA")
print("=" * 60)

ntl = pd.read_csv(
    r"G:\Village_Economic_Intelligence\viirs_annual_shrid.csv"
)

vd = pd.read_csv(
    r"C:\Users\Lenovo\Downloads\shrug-vd11-csv\pc11_vd_clean_shrid.csv"
)

anty = pd.read_csv(
    r"G:\Village_Economic_Intelligence\antyodaya_shrid.csv"
)

gee = pd.read_csv(
    r"C:\Users\Lenovo\Downloads\India_VIIRS_NTL_Growth_2019_2026.csv"
)

print(f"NTL rows loaded        : {len(ntl):,}")
print(f"Village directory rows : {len(vd):,}")
print(f"Antyodaya rows         : {len(anty):,}")



print("\nChecking required columns...")

required_ntl = [
    'shrid2',
    'year',
    'category',
    'viirs_annual_mean'
]

required_vd = [
    'shrid2',
    'pc11_vd_t_p',
    'pc11_vd_power_dom',
    'pc11_vd_rd_all_wthr'
]

required_anty = [
    'shrid2',
    'total_hhd',
    'total_hhd_have_got_pmay_house'
]

for col in required_ntl:
    if col not in ntl.columns:
        print(f"Missing NTL column: {col}")

for col in required_vd:
    if col not in vd.columns:
        print(f"Missing Village Directory column: {col}")

for col in required_anty:
    if col not in anty.columns:
        print(f"Missing Antyodaya column: {col}")

print("Column validation complete.")


print("\n" + "=" * 60)
print("BUILDING NTL GROWTH")
print("=" * 60)

print("Available categories:")
print(ntl['category'].unique())

ntl_vil = ntl[
    ntl['category'] == 'average-masked'
].copy()

print(f"Filtered NTL rows: {len(ntl_vil):,}")

ntl_2019 = ntl_vil[
    ntl_vil['year'] == 2019
][['shrid2', 'viirs_annual_mean']].copy()

ntl_2019.rename(
    columns={'viirs_annual_mean': 'ntl_2019'},
    inplace=True
)

ntl_2023 = ntl_vil[
    ntl_vil['year'] == 2023
][['shrid2', 'viirs_annual_mean']].copy()

ntl_2023.rename(
    columns={'viirs_annual_mean': 'ntl_2023'},
    inplace=True
)

ntl_growth = ntl_2019.merge(
    ntl_2023,
    on='shrid2',
    how='inner'
)

print(f"Villages with both years: {len(ntl_growth):,}")

# Log growth works better than raw ratio
ntl_growth['ntl_growth_ratio'] = (
    np.log1p(ntl_growth['ntl_2023']) -
    np.log1p(ntl_growth['ntl_2019'])
)

print("\nNTL growth stats:")
print(
    ntl_growth['ntl_growth_ratio']
    .describe()
    .round(3)
)

print("\n" + "=" * 60)
print("BUILDING INFRASTRUCTURE SCORE")
print("=" * 60)

vd_cols = [
    'shrid2',
    'pc11_vd_t_p',
    'pc11_vd_power_dom',
    'pc11_vd_rd_all_wthr',
    'pc11_vd_mobl_cov',
    'pc11_vd_comm_bank',
    'pc11_vd_mrkt',
    'pc11_vd_wkl_haat'
]

vd_cols = [c for c in vd_cols if c in vd.columns]

vd_small = vd[vd_cols].copy()

vd_small = vd_small.drop_duplicates(subset='shrid2')

vd_small['infra_score_raw'] = (
    vd_small.get('pc11_vd_power_dom', 0).fillna(0) * 30 +
    vd_small.get('pc11_vd_rd_all_wthr', 0).fillna(0) * 25 +
    vd_small.get('pc11_vd_mobl_cov', 0).fillna(0) * 20 +
    vd_small.get('pc11_vd_comm_bank', 0).fillna(0) * 10 +
    vd_small.get('pc11_vd_mrkt', 0).fillna(0) * 10 +
    vd_small.get('pc11_vd_wkl_haat', 0).fillna(0) * 5
)

print(
    f"Infrastructure score range: "
    f"{vd_small['infra_score_raw'].min()} "
    f"to "
    f"{vd_small['infra_score_raw'].max()}"
)



print("\n" + "=" * 60)
print("BUILDING HOUSING & SCHEME SCORE")
print("=" * 60)

anty_cols = [
    'shrid2',
    'total_hhd',
    'total_hhd_have_got_pmay_house',
    'total_hhd_with_kuccha_wall_kucch',
    'is_village_connected_to_all_weat',
    'availability_of_elect_supply_to_',
    'piped_water_fully_covered',
    'is_bank_available',
    'is_broadband_available',
    'total_shg'
]

anty_cols = [c for c in anty_cols if c in anty.columns]

anty_small = anty[anty_cols].copy()

anty_small = anty_small.drop_duplicates(subset='shrid2')

anty_small['pmay_density'] = (
    anty_small['total_hhd_have_got_pmay_house'].fillna(0)
    /
    anty_small['total_hhd'].replace(0, np.nan)
) * 100

anty_small['kuccha_rate'] = (
    anty_small['total_hhd_with_kuccha_wall_kucch'].fillna(0)
    /
    anty_small['total_hhd'].replace(0, np.nan)
)

anty_small['housing_score_raw'] = (
    anty_small['pmay_density'].fillna(0) * 0.6 +
    (1 - anty_small['kuccha_rate'].fillna(0.5)) * 40
)

anty_small['scheme_score_raw'] = (
    anty_small.get('is_village_connected_to_all_weat', 0).fillna(0) * 20 +
    anty_small.get('availability_of_elect_supply_to_', 0).fillna(0) * 20 +
    anty_small.get('piped_water_fully_covered', 0).fillna(0) * 15 +
    anty_small.get('is_broadband_available', 0).fillna(0) * 15 +
    anty_small.get('is_bank_available', 0).fillna(0) * 10 +
    anty_small.get('total_shg', 0).fillna(0).clip(upper=10) * 2
)

print(
    f"Housing score range: "
    f"{anty_small['housing_score_raw'].min():.2f} "
    f"to "
    f"{anty_small['housing_score_raw'].max():.2f}"
)


#CONNECTING DATASETS
print("\n" + "=" * 60)
print("JOINING DATASETS")
print("=" * 60)

df = ntl_growth.copy()

df = df.merge(
    vd_small,
    on='shrid2',
    how='left'
)

join_cols = [
    'shrid2',
    'pmay_density',
    'kuccha_rate',
    'housing_score_raw',
    'scheme_score_raw',
    'total_hhd'
]

join_cols = [c for c in join_cols if c in anty_small.columns]

df = df.merge(
    anty_small[join_cols],
    on='shrid2',
    how='left'
)

print(f"Final joined villages: {len(df):,}")

#SCORES
print("\n" + "=" * 60)
print("NORMALISING SCORES")
print("=" * 60)

def minmax(series):
    mn = series.min()
    mx = series.max()

    return ((series - mn) / (mx - mn + 1e-9)) * 100


lower_cap = df['ntl_growth_ratio'].quantile(0.01)
upper_cap = df['ntl_growth_ratio'].quantile(0.99)

df['ntl_growth_ratio_capped'] = (
    df['ntl_growth_ratio']
    .clip(lower=lower_cap, upper=upper_cap)
)

df['score_ntl'] = minmax(
    df['ntl_growth_ratio_capped']
)

df['score_infra'] = minmax(
    df['infra_score_raw'].fillna(0)
)

df['score_housing'] = minmax(
    df['housing_score_raw'].fillna(0)
)

df['score_market'] = minmax(
    df['scheme_score_raw'].fillna(0)
)

df['economic_growth_score'] = (
    0.40 * df['score_ntl'] +
    0.25 * df['score_infra'] +
    0.20 * df['score_housing'] +
    0.15 * df['score_market']
)

print("\nComposite score stats:")
print(
    df['economic_growth_score']
    .describe()
    .round(2)
)

print("\n" + "=" * 60)
print("RANKING VILLAGES")
print("=" * 60)

if 'pc11_vd_t_p' in df.columns:

    df = df[
        df['pc11_vd_t_p'].notna()
    ]

    df = df[
        df['pc11_vd_t_p'] > 0
    ]

print(f"Villages after filtering: {len(df):,}")

df = df.sort_values(
    'economic_growth_score',
    ascending=False
).reset_index(drop=True)

df['national_rank'] = df.index + 1

top100 = df.head(100).copy()

print("\nTop 10 villages:\n")

print(
    top100[
        [
            'national_rank',
            'shrid2',
            'economic_growth_score',
            'ntl_2019',
            'ntl_2023'
        ]
    ]
    .head(10)
    .to_string(index=False)
)


#sTATE INFORMATION
print("\n" + "=" * 60)
print("ADDING STATE INFORMATION")
print("=" * 60)

keys2 = pd.read_csv(
    r"G:\shrug-pc-keys-csv\pc11r_shrid_beta_key.csv"
)

state_map = {
    1: 'Jammu & Kashmir',
    2: 'Himachal Pradesh',
    3: 'Punjab',
    4: 'Chandigarh',
    5: 'Uttarakhand',
    6: 'Haryana',
    7: 'Delhi',
    8: 'Rajasthan',
    9: 'Uttar Pradesh',
    10: 'Bihar',
    11: 'Sikkim',
    12: 'Arunachal Pradesh',
    13: 'Nagaland',
    14: 'Manipur',
    15: 'Mizoram',
    16: 'Tripura',
    17: 'Meghalaya',
    18: 'Assam',
    19: 'West Bengal',
    20: 'Jharkhand',
    21: 'Odisha',
    22: 'Chhattisgarh',
    23: 'Madhya Pradesh',
    24: 'Gujarat',
    27: 'Maharashtra',
    28: 'Andhra Pradesh',
    29: 'Karnataka',
    30: 'Goa',
    32: 'Kerala',
    33: 'Tamil Nadu'
}

key_small = keys2[
    ['shrid2', 'pc11_state_id', 'pc11_district_id']
].copy()

top100 = top100.merge(
    key_small,
    on='shrid2',
    how='left'
)

top100['state_name'] = (
    top100['pc11_state_id']
    .map(state_map)
)

top100['district_id'] = (
    top100['shrid2']
    .str.split('-')
    .str[2]
)

top100['village_code'] = (
    top100['shrid2']
    .str.split('-')
    .str[4]
)

top100['village_label'] = (
    top100['state_name'].fillna('Unknown')
    + " / District-"
    + top100['district_id']
    + " / V-"
    + top100['village_code']
)

print("\nTop 10 labels:\n")

print(
    top100[
        [
            'national_rank',
            'village_label',
            'economic_growth_score'
        ]
    ]
    .head(10)
    .to_string(index=False)
)

# Exporting 

print("\n" + "=" * 60)
print("EXPORTING RESULTS")
print("=" * 60)

output_cols = [
    'national_rank',
    'shrid2',
    'state_name',
    'district_id',
    'village_label',
    'economic_growth_score',
    'score_ntl',
    'score_infra',
    'score_housing',
    'score_market',
    'ntl_2019',
    'ntl_2023',
    'ntl_growth_ratio_capped',
    'pc11_vd_t_p',
    'pmay_density',
    'kuccha_rate'
]

output_cols = [
    c for c in output_cols
    if c in top100.columns
]

top100[output_cols].to_csv(
    r"G:\Village_Economic_Intelligence\top100_villages_REAL.csv",
    index=False
)

all_output_cols = [
    c for c in output_cols
    if c in df.columns
]

df[all_output_cols].to_csv(
    r"G:\Village_Economic_Intelligence\all_villages_scored_REAL.csv",
    index=False
)

print("top100_villages_REAL.csv saved")
print("all_villages_scored_REAL.csv saved")

print("\nPipeline completed successfully.")
print(
    f"Top village score: "
    f"{top100['economic_growth_score'].iloc[0]:.2f}"
)
