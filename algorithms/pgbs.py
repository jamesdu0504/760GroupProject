from math import floor
import pandas as pd
import datasets.import_datasets as im #TODO:only here for testing purposes 
# from mlxtend.frequent_patterns import association_rules, fpgrowth

def psudo_graph(transactions):
    """
    Key
        prefix - out going edges
        postfix - in comming edges 
    """
    pg=dict()
    for transaction_id, transaction in enumerate(transactions):
        for i in range(len(transaction)):
            u=transaction[i]
            if i != len(transaction) - 1:
                v=transaction[i+1]
                if u not in pg:
                    pg[u]={"prefix":{transaction_id:v}, "postfix": dict()}
                else:
                    pg[u]["prefix"][transaction_id]=v
                if v not in pg:
                    pg[v]={"prefix":dict(), "postfix": {transaction_id:u}}
                else:
                    pg[v]["postfix"][transaction_id]=u
    return pg 

def psudo_graph_delete_item_transaction_pair(psudo_graph, pair):
    item, transaction =pair
    out_going_edge=None
    in_comming_edge=None

    if transaction in psudo_graph[item]["prefix"].keys():
        out_going_edge=psudo_graph[item]["prefix"][transaction]
        del psudo_graph[out_going_edge]["postfix"][transaction]
        del psudo_graph[item]["prefix"][transaction]
       
    if transaction in psudo_graph[item]["postfix"].keys():      
        in_comming_edge=psudo_graph[item]["postfix"][transaction]
        del psudo_graph[in_comming_edge]["prefix"][transaction]
        del psudo_graph[item]["postfix"][transaction]

    if in_comming_edge and out_going_edge:
        psudo_graph[in_comming_edge]["prefix"][transaction] = out_going_edge
        psudo_graph[out_going_edge]["postfix"][transaction] = in_comming_edge

def transactions_containing_itemset(psudo_graph, itemset):
    if len(itemset) == 0:
        transactions_containing_itemset=[]
    elif len(itemset) == 1 :
        transactions_containing_itemset=psudo_graph[itemset[0]]["prefix"].keys() | psudo_graph[itemset[0]]["postfix"].keys()
    else:
        transactions_containing_itemset=psudo_graph[itemset[0]]["prefix"].keys()
        for item in itemset[1:]:
            transactions_containing_itemset = transactions_containing_itemset & psudo_graph[item]["postfix"].keys()
        
    return transactions_containing_itemset


def items_in_transaction(psudo_graph, transaction):
    items = set()
    for k in psudo_graph.keys():
        if transaction in psudo_graph[k]['prefix'].keys() or transaction in psudo_graph[k]['postfix'].keys():
            items.add(k)

    return items


def support_count(psudo_graph, itemset):
    return len(transactions_containing_itemset(psudo_graph, itemset))

def sensitive_count_table(psudo_graph, sensitive_itemsets, d):
    """
    Table columns
        SID - the unique identifier 
        SI - the sensitive itemset
        N_modify - min num of transactions that need to be modified to hide the sensitive itemset   

    N_modify = floor (number of transactions containing X - (the sensitive support threshold * |database|+1)) 
    """
    sensitive_itemsets['n_modify'] = sensitive_itemsets.apply( lambda row: floor(support_count(psudo_graph, row.itemset) - (row.threshold *d)+1), axis=1)
    sensitive_itemsets.sort_values(by='n_modify', ascending=False, inplace=True)

def sanitization_table(psudo_graph, sensitive_itemsets, d):
    sanitization_tbl=[]
    sensitive_itemsets['itemset_set']=[set(itemset) for itemset in sensitive_itemsets['itemset']]
    while sensitive_itemsets.iloc[0]["n_modify"] !=0:
        itemset=sensitive_itemsets.iloc[0]["itemset"]
        victim_item=max([(item, support_count(psudo_graph,[item]), len(sensitive_itemsets.loc[(sensitive_itemsets['itemset_set'] >= set([item])) & (sensitive_itemsets['n_modify'] > 0)])) for item in itemset], key= lambda x: (x[2],x[1]))  #can change for faster implementation
        victim_item=victim_item[0]
        victim_item_in_a_set = {victim_item}
        sensitive_itemsets_with_victim_item=sensitive_itemsets.loc[(sensitive_itemsets['itemset_set']>= set([victim_item])) & (sensitive_itemsets["n_modify"]>0)].copy()
        sensitive_itemsets_with_victim_item.sort_values(by='n_modify', ascending=False, inplace=True)

        # end_pointer points to effective end of sensitive_itemsets_With_victim_item DF
        end_pointer = 0
        while True:
            victim_itemset=set([i
                                for itemset in sensitive_itemsets_with_victim_item['itemset'][:len(sensitive_itemsets_with_victim_item['itemset'])-end_pointer]
                                for i in itemset])  #victim_itemset is the union of the sensitive itemset contianing the victim item
            victim_itemset=sorted(list(victim_itemset))

            sensitive_transactions=list(transactions_containing_itemset(psudo_graph, victim_itemset)) #this will change

            set_zero=False
            while sensitive_itemsets.iloc[0]["n_modify"]>0 and sensitive_transactions: #we need to modify less than or equal to n_modify transactions
                pair=(victim_item, sensitive_transactions.pop())
                sanitization_tbl.append(pair)
                transaction_items = items_in_transaction(psudo_graph, pair[1])
                psudo_graph_delete_item_transaction_pair(psudo_graph, pair)
                
                for itemset_set in sensitive_itemsets_with_victim_item.loc[(sensitive_itemsets_with_victim_item["itemset_set"] <= transaction_items)]['itemset_set']:
                    old_nmodify = sensitive_itemsets.loc[sensitive_itemsets['itemset_set'] == itemset_set, 'n_modify'].item()
                    sensitive_itemsets.loc[sensitive_itemsets['itemset_set'] == itemset_set, 'n_modify'] -= 1
                    if old_nmodify == 1: # Then n_modify is now 0
                        set_zero = True
                if set_zero:
                    break

            if sensitive_itemsets.iloc[0]["n_modify"] == 0 or set_zero:
                sensitive_itemsets.sort_values(by='n_modify', ascending=False, inplace=True)
                set_zero = False
                break
            elif sensitive_itemsets.iloc[0]["n_modify"] < 0:
                raise Exception('n_modify < 0')
            else:
                # sensitive_itemsets_with_victim_item.drop(sensitive_itemsets_with_victim_item.tail(1).index, inplace = True)
                end_pointer += 1
    return sanitization_tbl

def pgbs(database, sensitive_itemsets):
    #preprocessing
    d=len(database.index)       #number of transactions
    db = im.convert_to_transaction(database, False)
    transactions=[row[1]["itemsets"] for row in db.iterrows()]
    sensitive_itemsets["itemset"]=sensitive_itemsets["itemset"].apply(lambda x: sorted(x))
    pg = psudo_graph(transactions)
    sensitive_count_table(pg, sensitive_itemsets, d)
    #selecting items to delete
    sanitization_tbl = sanitization_table(pg, sensitive_itemsets, d)
    #deleting items
    for item, transaction in sanitization_tbl:
        database.at[transaction, str(item)] = False
   
# database=im.import_dataset("toydata")
# #print(database)
# frequent_itemsets=fpgrowth(database, min_support=0.31, use_colnames=True) 
# #print(frequent_itemsets)
# data={'itemset':[['4'], ['1','2'], ['2','3']], 'threshold':[0.3, 0.25, 0.6]}
# sensitive_itemsets= pd.DataFrame(data)
# #print(sensitive_itemsets)
# pgbs(database,sensitive_itemsets)
# frequent_itemsets=fpgrowth(database, min_support=0.31, use_colnames=True) 
# print(frequent_itemsets)
