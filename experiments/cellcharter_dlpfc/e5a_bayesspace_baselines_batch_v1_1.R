# E5a BayesSpace 1.20.2 R script, minimal loader bugfix after 0/72 halted.
# 12 DLPFC slices x 3 technical seeds x 2 K arms = 72 saved predictions.
# Reads original 10x HDF5 CSC and spots_aligned.csv; joins by barcode.
# K-blind qTune(q=2..10, burn.in=100,nrep=1000, cores=1), max mean loglik.
# Fixed full spatialCluster 10,000 iterations (burn.in=1000, thin=100).
# Raw predictions of BOTH K arms are saved before reference layers opened.
# No training occurs unless command line has exactly --run.
# Fail closed: do not silently skip missing/corrupted input, no overwrites.

args <- commandArgs(trailingOnly = TRUE)
stopifnot(length(args) <= 1L)
if (!identical(args, "--run")) {
    cat("E5A_BAYESSPACE_PLAN samples=12 seeds=3 regimes=oracle_k,k_blind tasks=72 qs=2:10\n")
    cat("E5A_BAYESSPACE_DRY_RUN_ONLY NO_TRAINING_NO_FILES_WRITTEN\n")
    quit(save="no", status=0)
}

options(stringsAsFactors=FALSE, timeout=600L)
r_lib <- "D:/paper/CellCharter_reproduction/third_party/e5a_r_libs"
if (!dir.exists(r_lib)) stop("E5A_R_THIRD_PARTY_LIBRARY_MISSING")
.libPaths(c(r_lib, .libPaths()))

needed <- c("BayesSpace", "SingleCellExperiment", "SummarizedExperiment",
            "S4Vectors", "Matrix", "rhdf5", "digest", "jsonlite", "mclust")
for (pkg in needed) {
    if (!requireNamespace(pkg, quietly=TRUE)) {
        stop(paste("E5A_R_PACKAGE_NOT_INSTALLED",pkg))
    }
}
if (as.character(utils::packageVersion("BayesSpace")) != "1.20.2") {
    stop("E5A_BAYESSPACE_VERSION_NOT_FROZEN_1_20_2")
}

root <- "D:/paper/CellCharter_reproduction"
input_root <- "D:/paper/ST_Benchmark_Planning/mvp/data"
output_root <- file.path(root, "results/e5a_baselines_v1")
samples <- c("151507","151508","151509","151510","151669","151670",
             "151671","151672","151673","151674","151675","151676")
seeds <- c(22911L,7449L,25842L)
regimes <- c("oracle_k","k_blind")
expected_spots <- setNames(c(4226L,4384L,4789L,4634L,3661L,3498L,
                             4110L,4015L,3639L,3673L,3592L,3460L),samples)
expected_labeled <- setNames(c(4221L,4381L,4788L,4595L,3636L,3484L,
                               4093L,3888L,3611L,3635L,3566L,3431L),samples)
oracle_k <- setNames(ifelse(samples %in% c("151669","151670","151671","151672"),
                           5L,7L),samples)
q_grid <- 2L:10L
protocol <- "E5A_BAYESSPACE_ORACLE_KBLIND_V1"

assert <- function(test,msg) {
    if (!isTRUE(test)) stop(msg,call.=FALSE)
}
stamp <- function() format(Sys.time(), "%Y-%m-%dT%H:%M:%SZ", tz="UTC")
sha256 <- function(path) {
    assert(file.exists(path),"FILE_NOT_FOUND_FOR_SHA")
    unname(digest::digest(path,algo="sha256",file=TRUE))
}
save_json <- function(x,path) {
    jsonlite::write_json(x,path,pretty=TRUE,auto_unbox=TRUE,
                         null="null",na="null",digits=12)
}
save_table <- function(df,path) {
    utils::write.csv(df,path,row.names=FALSE,quote=TRUE,na="")
}
first_input <- function(sample) file.path(input_root,sample)

# Raw count loading only; manual annotations are intentionally NOT opened.
load_real_sce <- function(sample) {
    dir <- first_input(sample)
    spath <- file.path(dir,"spots_aligned.csv")
    h5path <- file.path(dir,"filtered_feature_bc_matrix.h5")
    refpath <- file.path(dir,"manual_layer_annotations.csv")
    assert(file.exists(spath) && file.exists(h5path) && file.exists(refpath),
           "BAYESSPACE_INPUT_FILE_MISSING")
    spots <- utils::read.csv(spath,check.names=FALSE,colClasses="character")
    assert(all(c("barcode","array_row","array_col") %in% names(spots)),
           "BAYESSPACE_SPOTS_COLUMN_MISSING")
    assert(nrow(spots)==expected_spots[[sample]] &&
           !anyDuplicated(spots$barcode) && !anyNA(spots$barcode),
           "BAYESSPACE_SPOT_COUNT_OR_DUPLICATE_BAD")
    row <- suppressWarnings(as.numeric(spots$array_row))
    col <- suppressWarnings(as.numeric(spots$array_col))
    assert(all(is.finite(row)) && all(is.finite(col)) &&
           all(row == floor(row)) && all(col == floor(col)),
           "BAYESSPACE_SPATIAL_ARRAY_COORDINATES_INVALID")
    assert(!anyDuplicated(paste(row,col,sep="_")),
           "BAYESSPACE_DUPLICATE_ARRAY_SPOT_POSITIONS")
    # TenX HDF5 CSC is feature x barcode, indices 0-based.
    dims <- as.integer(rhdf5::h5read(h5path,"matrix/shape"))
    ptr <- as.integer(rhdf5::h5read(h5path,"matrix/indptr"))
    ind <- as.integer(rhdf5::h5read(h5path,"matrix/indices"))
    val <- as.numeric(rhdf5::h5read(h5path,"matrix/data"))
    bc <- as.character(rhdf5::h5read(h5path,"matrix/barcodes"))
    gene <- as.character(rhdf5::h5read(h5path,"matrix/features/id"))
    assert(length(dims)==2L && dims[1]>2000 && dims[2]>3000 &&
           length(ptr)==dims[2]+1L && length(bc)==dims[2] &&
           length(gene)==dims[1] && length(ind)==length(val) &&
           length(ptr)>1L && ptr[1]==0L && tail(ptr,1)==length(val) &&
           !anyDuplicated(bc) && all(is.finite(val)) && all(val>=0),
           "BAYESSPACE_10X_CSC_STRUCTURE_INVALID")
    # 10x HDF5 CSC indices are 0-based and can be UNSORTED within columns.
    # Matrix::sparseMatrix canonicalizes/sorts them; it also sums duplicate
    # (feature, barcode) entries if any. Counts, barcodes and model unchanged.
    assert(all(diff(ptr) >= 0L) &&
           all(ind >= 0L) && all(ind < dims[1]),
           "BAYESSPACE_CSC_POINTER_OR_INDEX_INVALID")
    column_ix <- rep.int(seq_len(dims[2]), diff(ptr))
    assert(length(column_ix) == length(val),
           "BAYESSPACE_CSC_COLUMN_INDEX_LENGTH_BAD")
    mat <- Matrix::sparseMatrix(
        i=ind + 1L, j=column_ix, x=val, dims=dims,
        dimnames=list(make.unique(gene),bc),
        index1=TRUE, giveCsparse=TRUE)
    assert(methods::validObject(mat), "BAYESSPACE_CSC_CANONICAL_MATRIX_INVALID")
    rm(column_ix, ind, ptr, val)
    gc(verbose=FALSE)
    pos <- match(spots$barcode, bc)
    assert(!anyNA(pos), "BAYESSPACE_BARCODE_MISMATCH")
    mat <- mat[,pos,drop=FALSE]
    assert(ncol(mat)==expected_spots[[sample]] &&
           identical(colnames(mat), spots$barcode),
           "BAYESSPACE_REORDERED_SPOTS_INVALID")
    umi <- Matrix::colSums(mat)
    assert(all(is.finite(umi)) && all(umi>0),
           "BAYESSPACE_ZERO_UMI_OR_BAD_UMI_SPOT")
    cd <- S4Vectors::DataFrame(
        array_row=as.integer(row),
        array_col=as.integer(col),
        row.names=spots$barcode
    )
    sce <- SingleCellExperiment::SingleCellExperiment(
        assays=list(counts=mat),colData=cd)
    assert(identical(colnames(sce),spots$barcode),
           "BAYESSPACE_SCE_ORDER_CHANGED")
    source <- list(
        sample=sample,
        spots=normalizePath(spath,winslash="/",mustWork=TRUE),
        spots_sha256=sha256(spath),
        tenx_h5=normalizePath(h5path,winslash="/",mustWork=TRUE),
        tenx_h5_sha256=sha256(h5path),
        manual_label_file=normalizePath(refpath,winslash="/",mustWork=TRUE),
        manual_labels_opened=FALSE,
        spot_count=length(spots$barcode),
        genes=nrow(mat),
        spot_barcode_sha256=digest::digest(paste(spots$barcode,collapse="\n"),
                                          algo="sha256",serialize=FALSE),
        coordinates="array_row,array_col (original Visium hex lattice)",
        n_zero_umi=sum(umi==0)
    )
    list(sce=sce,barcodes=spots$barcode,source=source)
}

# Preprocessing uses fixed embedding seed; the 3 clustering seeds are technical.
make_preprocessed <- function(input) {
    set.seed(22911L)
    sce <- BayesSpace::spatialPreprocess(
        input$sce, platform="Visium",n.PCs=15L,n.HVGs=2000L,
        skip.PCA=FALSE,log.normalize=TRUE)
    embedded <- SingleCellExperiment::reducedDim(sce,"PCA")
    assert(nrow(embedded)==length(input$barcodes) && ncol(embedded)>=15 &&
           all(is.finite(embedded)), "BAYESSPACE_PREPROCESS_PCA_INVALID")
    assert(identical(colnames(sce),input$barcodes),
           "BAYESSPACE_PREPROCESS_REORDERED_SPOTS")
    sce
}

# This is a FROZEN automatic rule, distinct from BayesSpace authors' elbow guidance.
choose_q_blind <- function(sce,seed,out_dir) {
    set.seed(seed)
    tuned <- BayesSpace::qTune(
        sce,qs=q_grid,burn.in=100L,nrep=1000L,cores=1L,
        platform="Visium",d=15L,init.method="mclust",
        model="t",precision="equal")
    trace <- as.data.frame(attr(tuned,"q.logliks"))
    assert(all(c("q","loglik") %in% names(trace)) &&
           nrow(trace)==length(q_grid) &&
           identical(sort(as.integer(trace$q)),q_grid) &&
           all(is.finite(trace$loglik)),
           "BAYESSPACE_QTUNE_TRACE_INVALID")
    trace <- trace[order(as.integer(trace$q)),c("q","loglik")]
    trace$q <- as.integer(trace$q)
    save_table(trace,file.path(out_dir,"q_tune_all_K_2_to_10.csv"))
    highest <- max(trace$loglik)
    chosen <- min(trace$q[trace$loglik==highest])
    assert(length(chosen)==1L && chosen %in% q_grid,
           "BAYESSPACE_NO_VALID_BLIND_Q")
    list(q=as.integer(chosen),trace=trace)
}

cluster_fixed <- function(sce,q,seed) {
    set.seed(seed)
    fitted <- BayesSpace::spatialCluster(
        sce,q=as.integer(q),platform="Visium",d=15L,
        init.method="mclust",model="t",precision="equal",
        nrep=10000L,burn.in=1000L,thin=100L,save.chain=FALSE)
    col <- SummarizedExperiment::colData(fitted)
    assert("spatial.cluster" %in% names(col),
           "BAYESSPACE_CLUSTER_COLUMN_MISSING")
    lab <- as.integer(col$spatial.cluster)
    assert(length(lab)==ncol(sce) && !anyNA(lab) &&
           all(lab >= 1L) &&
           identical(colnames(fitted),colnames(sce)),
           "BAYESSPACE_OUTPUT_LABELS_INVALID_OR_REORDERED")
    lab
}

# Reference layer truth is loaded ONLY after BOTH original predictions are on disk.
reference_scores <- function(sample,barcodes,labels) {
    from <- file.path(first_input(sample),"manual_layer_annotations.csv")
    annotation <- utils::read.csv(from,check.names=FALSE,colClasses="character")
    assert(all(c("sample_name","spot_name","layer") %in% names(annotation)),
           "REFERENCE_HEADER_BAD")
    ann <- annotation[annotation$sample_name==sample,c("spot_name","layer")]
    assert(!anyDuplicated(ann$spot_name) && !anyNA(ann$layer),
           "REFERENCE_DUPLICATED_OR_MISSING")
    index <- match(barcodes,ann$spot_name)
    true <- ann$layer[index]
    valid <- !is.na(true) & nzchar(true)
    assert(sum(valid)==expected_labeled[[sample]] &&
           length(unique(true[valid]))==oracle_k[[sample]] &&
           length(labels)==length(barcodes),
           "REFERENCE_MASK_OR_K_INVALID")
    ari <- as.numeric(mclust::adjustedRandIndex(true[valid],labels[valid]))
    ct <- table(true[valid], as.character(labels[valid]))
    prob <- as.matrix(ct) / sum(ct)
    px <- rowSums(prob)
    py <- colSums(prob)
    product <- outer(px,py)
    nonzero <- prob > 0
    mi <- sum(prob[nonzero] * log(prob[nonzero] / product[nonzero]))
    hx <- -sum(px[px>0] * log(px[px>0]))
    hy <- -sum(py[py>0] * log(py[py>0]))
    nmi <- 2 * mi / (hx+hy)  # sklearn's arithmetic-mean NMI normalization
    assert(is.finite(ari) && is.finite(nmi) &&
           nmi >= -1e-9 && nmi <= 1+1e-9,
           "BAYESSPACE_EVALUATION_METRIC_NONFINITE")
    list(evaluated_spots=sum(valid),
         unlabeled_spots=sum(!valid),
         reference_sha256=sha256(from),
         ari=ari,nmi=as.numeric(nmi),
         metric_status="post_saved_predictions_true_barcode_aligned")
}

start <- stamp()
session <- file.path(output_root,
    paste0("bayesspace_",format(Sys.time(),"%Y%m%dT%H%M%SZ",tz="UTC"),
           "_",Sys.getpid()))
assert(!dir.exists(session),"BAYESSPACE_SESSION_PATH_ALREADY_EXISTS")
if (!dir.create(session,recursive=TRUE,showWarnings=FALSE)) {
    stop("BAYESSPACE_SESSION_CREATE_FAILED")
}
status_file <- file.path(session,"batch_status.json")
state <- list(
    protocol=protocol,status="running",started_utc=start,
    session=session,completed=0L,failed=0L,expected_tasks=72L,
    samples=samples,seeds=seeds,regimes=regimes,
    oracle_k_prior=as.list(oracle_k),
    q_blind_candidates=q_grid,
    q_blind_selection="maximize_mean_qTune_loglik_tie_smallest_q",
    q_blind_tune=list(nrep=1000L,burn_in=100L,cores=1L),
    full_run=list(nrep=10000L,burn_in=1000L,thin=100L,
                  model="t",precision="equal",init_method="mclust"),
    n_pcs=15L,n_hvgs=2000L,source="original_10x_counts",
    coordinate_system="Visium_array_row_array_col",
    preprocessing_seed=22911L,
    r_version=as.character(getRversion()),
    bayesspace_version=as.character(utils::packageVersion("BayesSpace")),
    compute_device="CPU",
    evaluation="only_after_both_predictions_saved; R mclust ARI and sklearn-equivalent NMI",
    tasks=list(),failure=NULL)
save_json(state,status_file)
completed <- 0L
task_id <- 0L

execute_all <- function() {
    for (sample in samples) {
        sample_start <- proc.time()[3]
        dir <- file.path(session,sample)
        assert(dir.create(dir,showWarnings=FALSE),"SAMPLE_OUTPUT_CREATE_FAILED")
        cat("E5A_BAYESSPACE_SAMPLE_START sample=",sample," expected=6\n",sep="")
        flush.console()
        original <- load_real_sce(sample)
        sce <- make_preprocessed(original)
        save_json(original$source,file.path(dir,"input_manifest.json"))
        original$sce <- NULL  # avoid retaining duplicate raw SCE in R memory
        gc(verbose=FALSE)
        for (seed in seeds) {
            seed_start <- proc.time()[3]
            run_dir <- file.path(dir,paste0("seed_",seed))
            assert(dir.create(run_dir,showWarnings=FALSE),
                   "SEED_OUTPUT_CREATE_FAILED")
            cat("E5A_BAYESSPACE_SEED_START sample=",sample,
                " seed=",seed," qtune=2:10\n",sep="")
            flush.console()
            tuned <- choose_q_blind(sce,seed,run_dir)
            # Each regime fitted with SAME declared technical seed, no labels.
            oracle_lab <- cluster_fixed(sce,oracle_k[[sample]],seed)
            blind_lab <- cluster_fixed(sce,tuned$q,seed)
            outputs <- list()
            # Both physically saved before opening manual annotations.
            for (regime in regimes) {
                lab <- if (regime=="oracle_k") oracle_lab else blind_lab
                target <- file.path(run_dir,regime)
                assert(dir.create(target,showWarnings=FALSE),
                       "REGIME_OUTPUT_CREATE_FAILED")
                prediction <- file.path(target,"predictions.csv")
                save_table(data.frame(barcode=original$barcodes,
                                      cluster=lab,check.names=FALSE),prediction)
                outputs[[regime]] <- list(prediction=prediction,labels=lab)
            }
            q_tune_sha <- sha256(file.path(run_dir,"q_tune_all_K_2_to_10.csv"))
            for (regime in regimes) {
                task_id <<- task_id+1L
                if (regime=="oracle_k") {
                    q <- as.integer(oracle_k[[sample]])
                    selection <- "reference_category_count_oracle_K"
                } else {
                    q <- tuned$q
                    selection <- "max_mean_qTune_pseudologlik_q_2_to_10"
                }
                labels <- outputs[[regime]]$labels
                metric <- reference_scores(sample,original$barcodes,labels)
                task <- list(
                    status="completed",method="BayesSpace",
                    sample=sample,regime=regime,seed=seed,
                    selected_q=q,actual_k=length(unique(labels)),
                    selection=selection,oracle_prior=as.integer(oracle_k[[sample]]),
                    candidate_trace=file.path(run_dir,"q_tune_all_K_2_to_10.csv"),
                    candidate_trace_sha256=q_tune_sha,
                    input_manifest=file.path(dir,"input_manifest.json"),
                    prediction_file=outputs[[regime]]$prediction,
                    prediction_sha256=sha256(outputs[[regime]]$prediction),
                    source_sample=sample,
                    metrics=metric,
                    wall_seconds_shared_seed=as.numeric(proc.time()[3]-seed_start),
                    finished_utc=stamp())
                manifest <- file.path(run_dir,regime,"manifest.json")
                save_json(task,manifest)
                state$tasks[[length(state$tasks)+1L]] <<- list(
                    sample=sample,seed=seed,regime=regime,
                    status="completed",manifest=manifest)
                completed <<- completed+1L
                state$completed <<- completed
                save_json(state,status_file)
                cat(sprintf(
                    "E5A_BAYESSPACE_PASS %d/72 sample=%s regime=%s seed=%d q=%d actual_k=%d\n",
                    task_id,sample,regime,seed,q,length(unique(labels))))
                flush.console()
            }
            rm(tuned,oracle_lab,blind_lab,outputs)
            gc(verbose=FALSE)
        }
        cat(sprintf("E5A_BAYESSPACE_SAMPLE_PASS sample=%s seconds=%.2f\n",
                    sample,proc.time()[3]-sample_start))
        rm(sce,original)
        gc(verbose=FALSE)
    }
}

tryCatch(
    {
        execute_all()
        assert(completed==72L && task_id==72L, "TASK_COUNT_NOT_72")
        state$status <- "completed"
        state$finished_utc <- stamp()
        save_json(state,status_file)
        cat("E5A_BAYESSPACE_FINAL status=completed completed=72/72 failed=0 summary=",
            status_file,"\n",sep="")
    },
    error=function(e) {
        state$status <<- "halted"
        state$failed <<- 1L
        state$failure <<- list(message=conditionMessage(e),utc=stamp())
        state$finished_utc <<- stamp()
        save_json(state,status_file)
        cat("E5A_BAYESSPACE_HALTED completed=",completed,
            "/72 error=",conditionMessage(e),
            " summary=",status_file,"\n",sep="",file=stderr())
        quit(save="no",status=2)
    }
)
