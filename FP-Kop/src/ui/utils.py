from collections import namedtuple

Routes = namedtuple(
    "ROUTES",
    [
        "DASHBOARD",
        "MOST_SOLD",
        "SHOW",
        "SHOW_ITEM",
        "SHOW_TRANSACTION",
        "SHOW_TRANSACTION_UPDATE",
        "SHOW_RESULT",
        "SHOW_RULES",
        "INPUT",
        "INPUT_ITEM",
        "INPUT_TRANSACTION",
        "PROCESS",
        "PROCESS_ITEM",
        "PROCESS_TRANSACTION",
        "RESULT",
        "RESULT_ITEMSET",
        "RESULT_STRATEGY",
        "RESULT_RULES",
    ],
)
ROUTES = Routes(
    DASHBOARD="/",
    MOST_SOLD="/most_sold",
    SHOW="/show",
    SHOW_ITEM="/show/item",
    SHOW_TRANSACTION="/show/transaction",
    SHOW_TRANSACTION_UPDATE="/show/transaction/update",
    SHOW_RULES="/show/rules",
    SHOW_RESULT="/show/result",
    INPUT="/ipnut",
    INPUT_ITEM="/input/item",
    INPUT_TRANSACTION="/input/transaction",
    PROCESS="/process",
    PROCESS_ITEM="/process/item",
    PROCESS_TRANSACTION="/process/transaction",
    RESULT="/result",
    RESULT_ITEMSET="/result/itemset",
    RESULT_RULES="/result/rules",
    RESULT_STRATEGY="/result/strategy",
    
)

Color = namedtuple("COLORS", ["PRIMARY", "SECONDARY", "TERTIARY", "CONTRAST", "DARK", "PRIMARY_DARK", "BASE_DARK"])
COLORS = Color(
    DARK="#1A1F2B",
    CONTRAST="#D18C47",
    PRIMARY="#23304C",
    SECONDARY="#6A7C9E",
    TERTIARY="#A1B1D0",
    PRIMARY_DARK="#171717",
    BASE_DARK="#212121",
)

Tables = namedtuple(
    "TABLES",
    [
        "BARANG",
        "TRANSAKSI",
        "DETAIL_TRANSAKSI",
        "HASIL_ANALISIS",
        "ASSOCIATION_RULES",
        "ANTECEDENTS",
        "CONSEQUENTS",
    ],
)
TABLES = Tables(
    ANTECEDENTS="antecedents",
    ASSOCIATION_RULES="association_rules",
    BARANG="barang",
    CONSEQUENTS="consequents",
    DETAIL_TRANSAKSI="detail_transaksi",
    HASIL_ANALISIS="hasil_analisis",
    TRANSAKSI="transaksi",
)

def formated_currency(currency):
    return (
        "Rp{:,.2f}".format(currency).replace(",", "X").replace(".", ",").replace("X", ".")
    )