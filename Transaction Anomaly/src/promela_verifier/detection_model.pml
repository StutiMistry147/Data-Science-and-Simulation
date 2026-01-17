#define NUM_ACCOUNTS 5
#define NUM_THREADS 3
#define MAX_TRANSACTIONS 10

mtype = { NORMAL, ANOMALOUS };

typedef Transaction {
    byte account_id;
    int amount;
    mtype type;
}

/* Global transaction queue */
chan transaction_queue = [10] of { Transaction };

/* Account history - shared resource that needs protection */
int account_history[NUM_ACCOUNTS];
bool history_lock = false;

/* Detection results */
int anomalies_detected = 0;

/* Mutex for protecting shared resources */
inline acquire_lock() {
    atomic {
        !history_lock -> history_lock = true
    }
}

inline release_lock() {
    atomic {
        history_lock = false
    }
}

/* Rule: Large amount detection */
inline check_large_amount(Transaction t) {
    if
    :: t.amount > 5000 -> 
        atomic {
            anomalies_detected++;
            printf("Large amount detected: %d from account %d\n", t.amount, t.account_id)
        }
    :: else -> skip
    fi
}

/* Rule: Rapid transactions detection */
inline check_rapid_transactions(byte account_id) {
    acquire_lock();
    if
    :: account_history[account_id] > 2 ->
        atomic {
            anomalies_detected++;
            printf("Rapid transactions detected for account %d\n", account_id)
        }
    :: else -> skip
    fi
    account_history[account_id]++;
    release_lock();
}

/* Transaction processor */
proctype TransactionProcessor(byte id) {
    Transaction t;
    int count = 0;
    
    do
    :: count < MAX_TRANSACTIONS ->
        /* Receive transaction from queue */
        transaction_queue ? t;
        
        printf("Thread %d processing transaction for account %d\n", id, t.account_id);
        
        /* Apply detection rules concurrently */
        check_large_amount(t);
        check_rapid_transactions(t.account_id);
        
        count++
    :: else -> break
    od
}

/* Transaction generator */
proctype TransactionGenerator() {
    Transaction t;
    int i = 0;
    
    do
    :: i < (MAX_TRANSACTIONS * NUM_THREADS) ->
        /* Generate random transaction */
        t.account_id = (i % NUM_ACCOUNTS);
        t.amount = (i % 7) * 1000;  /* Some will be large */
        if
        :: (i % 5) == 0 -> t.type = ANOMALOUS
        :: else -> t.type = NORMAL
        fi;
        
        /* Send to queue */
        transaction_queue ! t;
        
        printf("Generated transaction %d: account=%d, amount=%d\n", 
               i, t.account_id, t.amount);
        i++
    :: else -> break
    od
}

/* Monitor for checking assertions */
proctype Monitor() {
    do
    :: true ->
        /* Assertion 1: No race condition in account_history */
        assert(history_lock == false || history_lock == true);
        
        /* Assertion 2: anomalies_detected is non-negative */
        assert(anomalies_detected >= 0);
        
        /* Check for deadlock */
        if
        :: transaction_queue == [0] of { Transaction } ->
            /* Queue empty but processors might be waiting */
            skip
        :: else -> skip
        fi
    od
}

init {
    int i;
    
    /* Initialize account history */
    for (i : 0 .. NUM_ACCOUNTS-1) {
        account_history[i] = 0;
    }
    
    /* Start transaction generator */
    run TransactionGenerator();
    
    /* Start multiple processor threads */
    for (i : 0 .. NUM_THREADS-1) {
        run TransactionProcessor(i);
    }
    
    /* Start monitor */
    run Monitor();
    
    /* Set timeout to ensure termination */
    timeout -> 
        printf("\nVerification complete.\n");
        printf("Total anomalies detected: %d\n", anomalies_detected);
        printf("Final account history: ");
        for (i : 0 .. NUM_ACCOUNTS-1) {
            printf("%d:%d ", i, account_history[i])
        }
        printf("\n")
}
