# E5b BayesSpace 1.20.2 frozen six-patient external baseline.
# Exact E5a v1.1 BayesSpace method settings; only source adapts from 10x H5
# to already staged, MD5/SHA-verified Wu et al. 2021 MatrixMarket files.
# Six independent patients x three seeds x two K arms = 36 predictions.
# K-blind: qTune qs=2:10, burn.in=100, nrep=1000; max loglik, tie lower q.
# Oracle: fixed predeclared label-category-count q. Both arms use
# spatialCluster nrep=10000, burn.in=1000, thin=100, t model, mclust.
# Does NOT read reference_labels, classification, or compute ARI/NMI.
# Child process per patient; new isolated attempt dirs, no overwrites.
# --run for full batch. --resume <halted_session> explicit resume only.
# Not yet run on the user's Windows environment.

args <- commandArgs(trailingOnly=TRUE)
if (length(args)==0L) {
    cat("E5B_BAYESSPACE_DRY_RUN six_patients=6 seeds=3 arms=2 predictions=36\n")
    cat("NO_FILES_WRITTEN_NO_TRAINING_NO_REFERENCE_LABELS\n")
    quit(save="no", status=0L)
}
if (!((length(args)==1L && identical(args[1], "--run")) ||
      (length(args)==2L && identical(args[1], "--resume")) ||
      (length(args)==3L && identical(args[1], "--child")))) {
    stop("E5B_BAYESSPACE_ARGUMENTS_INVALID", call.=FALSE)
}

options(stringsAsFactors=FALSE, timeout=600L)
root <- "D:/paper/CellCharter_reproduction"
out_root <- file.path(root, "results/e5b_external_v1")
stage_dir <- file.path(out_root, "input_stage_20261121T083911Z_14272")
r_lib <- file.path(root, "third_party/e5a_r_libs")
if (!dir.exists(r_lib)) stop("E5B_R_THIRD_PARTY_LIBRARY_MISSING", call.=FALSE)
.libPaths(c(r_lib, .libPaths()))
needed <- c("BayesSpace", "SingleCellExperiment",
            "SummarizedExperiment", "S4Vectors", "Matrix",
            "digest", "jsonlite", "mclust")
for (pkg in needed) {
    if (!requireNamespace(pkg, quietly=TRUE)) {
        stop(paste("E5B_R_REQUIRED_PACKAGE_MISSING", pkg), call.=FALSE)
    }
}
if (as.character(utils::packageVersion("BayesSpace")) != "1.20.2") {
    stop("E5B_BAYESSPACE_VERSION_NOT_FROZEN_1_20_2", call.=FALSE)
}

samples <- c("1142243F", "1160920F", "CID4290",
             "CID4465", "CID44971", "CID4535")
n_spots <- stats::setNames(
    c(4784L, 4895L, 2426L, 1211L, 1160L, 1125L), samples)
n_genes <- stats::setNames(
    c(28402L, 28402L, 19237L, 19237L, 19237L, 19237L), samples)
oracle_k <- stats::setNames(c(5L, 7L, 3L, 3L, 6L, 6L), samples)
seeds <- c(22911L, 7449L, 25842L)
arms <- c("k_blind", "oracle_k")
q_grid <- 2L:10L
protocol <- "E5B_BAYESSPACE_FROZEN_SIX_PATIENTS_V1"

require <- function(ok, msg) {
    if (!isTRUE(ok)) stop(msg, call.=FALSE)
}
stamp <- function() format(Sys.time(), "%Y-%m-%dT%H:%M:%SZ", tz="UTC")
utc_id <- function() format(Sys.time(), "%Y%m%dT%H%M%SZ", tz="UTC")
sha256 <- function(path) {
    require(file.exists(path), paste("E5B_BS_SHA_SOURCE_MISSING", path))
    unname(digest::digest(path, algo="sha256", file=TRUE))
}
save_json <- function(obj, path) {
    jsonlite::write_json(obj, path, pretty=TRUE, auto_unbox=TRUE,
                         null="null", na="null", digits=12)
}
save_table <- function(df, path) {
    utils::write.csv(df, path, row.names=FALSE, quote=TRUE, na="")
}
new_dir <- function(path, parent=FALSE) {
    require(!dir.exists(path), paste("E5B_BS_OUTPUT_EXISTS",path))
    require(dir.create(path, recursive=parent, showWarnings=FALSE),
            paste("E5B_BS_CREATE_OUTPUT_FAILED",path))
}

load_stage <- function() {
    file <- file.path(stage_dir, "batch_status.json")
    require(file.exists(file), "E5B_BS_SOURCE_STAGE_MISSING")
    s <- jsonlite::fromJSON(file, simplifyVector=FALSE)
    require(identical(s$status,"completed") &&
            as.integer(s$total_model_spots)==15601L &&
            as.integer(s$total_eval_spots)==15324L &&
            length(s$samples)==6L &&
            identical(vapply(s$samples, function(x) x$sample, character(1)),samples),
            "E5B_BS_SOURCE_STAGE_NOT_COMPLETED")
    list(status=s, sha256=sha256(file))
}

# Count and coordinates only; intentionally never access the reference-only folder.
load_real_sce <- function(sample, entry) {
    src <- file.path(stage_dir, "inputs", sample)
    filenames <- c("matrix.mtx", "features.tsv", "barcodes.tsv",
                   "model_spots.csv")
    for (name in filenames) {
        p <- file.path(src, name)
        require(file.exists(p),paste("E5B_BS_INPUT_MISSING",sample,name))
        require(identical(sha256(p), entry$input_files_sha256[[name]]),
                paste("E5B_BS_INPUT_SHA_MISMATCH",sample,name))
    }
    spath <- file.path(src, "model_spots.csv")
    matpath <- file.path(src, "matrix.mtx")
    featpath <- file.path(src, "features.tsv")
    bcpath <- file.path(src, "barcodes.tsv")

    spots <- utils::read.csv(spath, check.names=FALSE,
                             colClasses="character", stringsAsFactors=FALSE)
    require(all(c("barcode","array_row","array_col") %in% names(spots)) &&
            nrow(spots)==n_spots[[sample]] &&
            !anyDuplicated(spots$barcode) && !anyNA(spots$barcode) &&
            all(nzchar(spots$barcode)),
            paste("E5B_BS_BARCODE_OR_SPOT_TABLE_INVALID", sample))
    r <- suppressWarnings(as.numeric(spots$array_row))
    c <- suppressWarnings(as.numeric(spots$array_col))
    require(all(is.finite(r)) && all(is.finite(c)) &&
            all(r==floor(r)) && all(c==floor(c)) &&
            !anyDuplicated(paste(r,c,sep="_")),
            paste("E5B_BS_GRID_COORDINATES_BAD",sample))

    bc <- readLines(bcpath, warn=FALSE, encoding="UTF-8")
    require(length(bc)>0L && !anyNA(bc) &&
            all(nzchar(bc)) && !anyDuplicated(bc),
            paste("E5B_BS_RAW_BARCODES_INVALID",sample))
    feat <- utils::read.delim(
        featpath, header=FALSE, sep="\t", quote="", comment.char="",
        colClasses="character", stringsAsFactors=FALSE, check.names=FALSE)
    require(nrow(feat)==n_genes[[sample]] && ncol(feat)%in%c(2L,3L) &&
            !anyNA(feat[[1]]) && all(nzchar(feat[[1]])) &&
            !anyDuplicated(feat[[1]]),
            paste("E5B_BS_RAW_FEATURES_INVALID",sample))

    # 10x MatrixMarket is features x barcodes. Conversion through Matrix
    # canonicalizes sparse column indices as in E5a v1.1's CSC loader fix.
    mat <- Matrix::readMM(matpath)
    require(nrow(mat)==n_genes[[sample]] && ncol(mat)==length(bc),
            paste("E5B_BS_RAW_MTX_DIMENSIONS_CHANGED",sample))
    mat <- methods::as(mat, "dgCMatrix")
    require(methods::validObject(mat) &&
            all(is.finite(mat@x)) && all(mat@x>=0),
            paste("E5B_BS_MTX_SPARSE_COUNTS_INVALID",sample))
    dimnames(mat) <- list(make.unique(feat[[1]]),bc)
    ix <- match(spots$barcode,bc)
    require(!anyNA(ix),paste("E5B_BS_MTX_BARCODE_ALIGNMENT_BAD",sample))
    mat <- mat[,ix,drop=FALSE]
    require(ncol(mat)==n_spots[[sample]] &&
            identical(colnames(mat),spots$barcode),
            paste("E5B_BS_MODEL_SPOT_COLUMN_ORDER_BAD",sample))
    umi <- Matrix::colSums(mat)
    require(all(is.finite(umi)) && all(umi>0),
            paste("E5B_BS_ZERO_UMI_MODEL_SPOT",sample))

    cd <- S4Vectors::DataFrame(array_row=as.integer(r),
                               array_col=as.integer(c),
                               row.names=spots$barcode)
    sce <- SingleCellExperiment::SingleCellExperiment(
        assays=list(counts=mat),colData=cd)
    require(identical(colnames(sce),spots$barcode),
            paste("E5B_BS_SCE_BARCODE_ORDER_CHANGED",sample))
    source <- list(
        sample=sample,
        stage_path=normalizePath(src, winslash="/", mustWork=TRUE),
        source_file_sha256=entry$input_files_sha256,
        model_spots=ncol(mat),genes=nrow(mat),
        n_zero_umi=sum(umi==0),
        coordinates="frozen in-tissue Visium array_row,array_col",
        reference_labels_read=FALSE)
    rm(mat)
    gc(verbose=FALSE)
    list(sce=sce,barcodes=spots$barcode,source=source)
}

make_preprocessed <- function(input) {
    set.seed(22911L)
    sce <- BayesSpace::spatialPreprocess(
        input$sce,platform="Visium",n.PCs=15L,n.HVGs=2000L,
        skip.PCA=FALSE,log.normalize=TRUE)
    reduced <- SingleCellExperiment::reducedDim(sce,"PCA")
    require(nrow(reduced)==length(input$barcodes) &&
            ncol(reduced)>=15L && all(is.finite(reduced)) &&
            identical(colnames(sce),input$barcodes),
            "E5B_BS_PCA15_OR_SPOT_ORDER_BAD")
    sce
}

choose_q_blind <- function(sce,seed,out_dir) {
    set.seed(seed)
    tuned <- BayesSpace::qTune(
        sce,qs=q_grid,burn.in=100L,nrep=1000L,cores=1L,
        platform="Visium",d=15L,init.method="mclust",
        model="t",precision="equal")
    trace <- as.data.frame(attr(tuned,"q.logliks"))
    require(all(c("q","loglik") %in% names(trace)) &&
            nrow(trace)==length(q_grid) &&
            identical(sort(as.integer(trace$q)),q_grid) &&
            all(is.finite(trace$loglik)),
            "E5B_BS_QTUNE_TRACE_INVALID")
    trace <- trace[order(as.integer(trace$q)),c("q","loglik")]
    trace$q <- as.integer(trace$q)
    save_table(trace,file.path(out_dir,"q_tune_all_K_2_to_10.csv"))
    highest <- max(trace$loglik)
    chosen <- min(trace$q[trace$loglik==highest])
    require(length(chosen)==1L && chosen %in% q_grid,
            "E5B_BS_NO_VALID_KBLIND_Q")
    list(q=as.integer(chosen),trace=trace)
}

cluster_fixed <- function(sce,q,seed) {
    set.seed(seed)
    fitted <- BayesSpace::spatialCluster(
        sce,q=as.integer(q),platform="Visium",d=15L,
        init.method="mclust",model="t",precision="equal",
        nrep=10000L,burn.in=1000L,thin=100L,save.chain=FALSE)
    cd <- SummarizedExperiment::colData(fitted)
    require("spatial.cluster" %in% names(cd),
            "E5B_BS_SPATIAL_CLUSTER_COLUMN_MISSING")
    lab <- as.integer(cd$spatial.cluster)
    require(length(lab)==ncol(sce) && !anyNA(lab) &&
            all(lab >= 1L) &&
            identical(colnames(fitted),colnames(sce)),
            "E5B_BS_PREDICTION_INVALID_OR_SPOTS_REORDERED")
    lab
}

check_finished_attempt <- function(dir,sample) {
    mf <- file.path(dir,"sample_manifest.json")
    require(file.exists(mf),"E5B_BS_SAMPLE_MANIFEST_MISSING")
    m <- jsonlite::fromJSON(mf,simplifyVector=FALSE)
    require(identical(m$status,"completed") &&
            identical(m$protocol,protocol) &&
            identical(m$sample,sample) &&
            length(m$tasks)==6L,
            "E5B_BS_SAMPLE_MANIFEST_NOT_COMPLETED")
    expected <- as.character(as.vector(t(outer(as.character(seeds),
                                               arms,paste,sep=":"))))
    actual <- vapply(m$tasks, function(x)
        paste(x$seed,x$arm,sep=":"), character(1))
    # The exact canonical order: seed 22911, both arms; seed 7449, both arms; etc.
    expected <- unlist(lapply(seeds,function(seed)
        paste(seed,arms,sep=":")),use.names=FALSE)
    require(identical(actual,expected),
            "E5B_BS_SAMPLE_TASKS_NOT_EXPECTED_SEED_ARM_GRID")
    for (item in m$tasks) {
        pp <- file.path(dir,item$predictions_file)
        require(file.exists(pp) && identical(sha256(pp),item$prediction_sha256),
                "E5B_BS_EXISTING_PREDICTION_SHA_CHANGED")
        qtune <- file.path(dir,item$q_tune_file)
        require(file.exists(qtune) && identical(sha256(qtune),item$q_tune_sha256),
                "E5B_BS_EXISTING_QTUNE_SHA_CHANGED")
    }
    m
}

run_sample <- function(sample,session,stage) {
    idx <- match(sample,samples)
    require(!is.na(idx), "E5B_BS_UNKNOWN_SAMPLE")
    entry <- stage$status$samples[[idx]]
    parent <- file.path(session,sample)
    if (!dir.exists(parent)) {
        require(dir.create(parent,recursive=FALSE,showWarnings=FALSE),
                "E5B_BS_PATIENT_DIRECTORY_CREATE_FAILED")
    }
    run_dir <- file.path(parent,paste0(
        "attempt_",format(Sys.time(),"%Y%m%dT%H%M%OS6Z",tz="UTC"),
        "_",Sys.getpid()))
    run_dir <- gsub(":", "", run_dir, fixed=TRUE)
    new_dir(run_dir)
    mf <- file.path(run_dir,"sample_manifest.json")
    state <- list(
        status="running",protocol=protocol,sample=sample,
        started_utc=stamp(),stage_sha256=stage$sha256,
        technical_seeds=as.list(seeds),arms=as.list(arms),
        oracle_k_is_label_count_informed=TRUE,
        reference_labels_read=FALSE,metrics_computed=FALSE,
        preproc_seed=22911L,preproc=list(
            platform="Visium",n_PCs=15L,n_HVGs=2000L,log_normalize=TRUE),
        q_tune=list(qs=as.list(q_grid),burn_in=100L,nrep=1000L,cores=1L,
                    criterion="maximum_q_loglik_tie_smallest_q"),
        cluster=list(nrep=10000L,burn_in=1000L,thin=100L,
                     init_method="mclust",model="t",precision="equal"),
        r_version=as.character(getRversion()),
        bayesspace_version=as.character(utils::packageVersion("BayesSpace")),
        expected_tasks=6L,tasks=list())
    save_json(state,mf)
    t0 <- proc.time()[3]
    tryCatch({
        input <- load_real_sce(sample,entry)
        sce <- make_preprocessed(input)
        save_json(input$source,file.path(run_dir,"source_manifest.json"))
        input$sce <- NULL
        gc(verbose=FALSE)
        for (seed in seeds) {
            seed_dir <- file.path(run_dir,paste0("seed_",seed))
            new_dir(seed_dir)
            cat(sprintf("E5B_BS_SEED_START sample=%s seed=%s qtune=2:10\n",
                        sample,seed))
            tuned <- choose_q_blind(sce,seed,seed_dir)
            # Both arms use fixed true category count only for oracle comparator.
            labels_oracle <- cluster_fixed(sce,oracle_k[[sample]],seed)
            labels_blind <- cluster_fixed(sce,tuned$q,seed)
            qfile <- file.path(seed_dir,"q_tune_all_K_2_to_10.csv")
            # Save BOTH predictions before any downstream evaluation. We never
            # open a reference file in this script.
            for (arm in arms) {
                target <- file.path(seed_dir,arm)
                new_dir(target)
                selected_q <- if (arm=="oracle_k") oracle_k[[sample]] else tuned$q
                labels <- if (arm=="oracle_k") labels_oracle else labels_blind
                predfile <- file.path(target,"predictions.csv")
                save_table(data.frame(barcode=input$barcodes,cluster=labels),
                           predfile)
                record <- list(
                    seed=as.integer(seed),arm=arm,
                    selected_q=as.integer(selected_q),
                    actual_k=as.integer(length(unique(labels))),
                    q_selection=if (arm=="oracle_k")
                        "reference_class_count_oracle" else
                        "qTune_maximum_mean_loglik_tie_smallest_q",
                    predictions_file=paste0("seed_",seed,"/",arm,"/predictions.csv"),
                    prediction_sha256=sha256(predfile),
                    q_tune_file=paste0(
                        "seed_",seed,"/q_tune_all_K_2_to_10.csv"),
                    q_tune_sha256=sha256(qfile),
                    wall_seconds_shared_seed=NA_real_)
                state$tasks[[length(state$tasks)+1L]] <- record
                save_json(state,mf)
                cat(sprintf("E5B_BS_PREDICTION_PASS sample=%s arm=%s seed=%d q=%d actual_k=%d\n",
                            sample,arm,seed,selected_q,record$actual_k))
            }
            rm(tuned,labels_oracle,labels_blind)
            gc(verbose=FALSE)
        }
        require(length(state$tasks)==6L,"E5B_BS_SIX_TASKS_NOT_COMPLETED")
        state$status <- "completed"
        state$seconds <- as.numeric(proc.time()[3]-t0)
        state$finished_utc <- stamp()
        save_json(state,mf)
        check_finished_attempt(run_dir,sample)
        cat(sprintf("E5B_BS_SAMPLE_PASS sample=%s tasks=6 seconds=%.2f result=%s\n",
                    sample,state$seconds,run_dir))
    }, error=function(e) {
        state$status <<- "failed"
        state$error <<- conditionMessage(e)
        state$failed_utc <<- stamp()
        save_json(state,mf)
        cat(sprintf("E5B_BS_SAMPLE_FAILED sample=%s error=%s result=%s\n",
                    sample,conditionMessage(e),run_dir),file=stderr())
        stop(e)
    })
}

execute <- function(session=NULL) {
    stage <- load_stage()
    if (is.null(session)) {
        session <- file.path(out_root,paste0(
            "bayesspace_",utc_id(),"_",Sys.getpid()))
        new_dir(session,parent=TRUE)
        state <- list(
            protocol=protocol,status="running",started_utc=stamp(),
            stage_batch_sha256=stage$sha256,
            expected_samples=as.list(samples),expected_tasks=36L,
            completed_samples=list(),failures=list(),
            reference_labels_read=FALSE,metrics_computed=FALSE,
            bayesspace_version=as.character(utils::packageVersion("BayesSpace")))
    } else {
        require(dir.exists(session),"E5B_BS_RESUME_SESSION_MISSING")
        mf <- file.path(session,"batch_status.json")
        require(file.exists(mf),"E5B_BS_RESUME_STATUS_MISSING")
        state <- jsonlite::fromJSON(mf,simplifyVector=FALSE)
        require(identical(state$protocol,protocol) &&
                identical(state$status,"halted") &&
                identical(state$stage_batch_sha256,stage$sha256) &&
                as.integer(state$expected_tasks)==36L,
                "E5B_BS_RESUME_NOT_ALLOWED")
        state$status <- "running"
        state$resumed_utc <- stamp()
    }
    statusfile <- file.path(session,"batch_status.json")
    save_json(state,statusfile)
    done <- character(0)
    if (length(state$completed_samples)>0L) {
        done <- vapply(state$completed_samples,function(x) x$sample,character(1))
    }
    tryCatch({
        for (sample in samples) {
            if (sample %in% done) {
                rec <- state$completed_samples[[match(sample,done)]]
                check_finished_attempt(rec$attempt,sample)
                cat(sprintf("E5B_BS_REUSED_VERIFIED sample=%s\n",sample))
                next
            }
            cat(sprintf("E5B_BS_SAMPLE_START sample=%s expected_tasks=6\n",
                        sample))
            flush.console()
            script_arg <- grep("^--file=",commandArgs(trailingOnly=FALSE),
                               value=TRUE)
            require(length(script_arg)==1L,"E5B_BS_SCRIPT_PATH_MISSING")
            script_path <- sub("^--file=","",script_arg[[1L]])
            script_path <- normalizePath(script_path,winslash="/",mustWork=TRUE)
            rscript <- file.path(R.home("bin"),"Rscript.exe")
            require(file.exists(rscript),"E5B_BS_CHILD_RSCRIPT_MISSING")
            child_args <- c("--vanilla",script_path,"--child",sample,
                            normalizePath(session,winslash="/",mustWork=TRUE))
            result <- suppressWarnings(system2(rscript,args=child_args,
                                               stdout="",stderr=""))
            require(length(result)==1L && result==0L,
                    sprintf("E5B_BS_CHILD_FAILED sample=%s exit=%s",
                            sample,paste(result,collapse=",")))
            parent <- file.path(session,sample)
            attempts <- list.dirs(parent,recursive=FALSE,full.names=TRUE)
            attempts <- attempts[grepl("^attempt_",basename(attempts))]
            success <- Filter(function(path) {
                f <- file.path(path,"sample_manifest.json")
                if (!file.exists(f)) return(FALSE)
                m <- tryCatch(jsonlite::fromJSON(f,simplifyVector=FALSE),
                              error=function(e) NULL)
                !is.null(m) && identical(m$status,"completed")
            },attempts)
            require(length(success)==1L,
                    paste("E5B_BS_COMPLETED_ATTEMPT_AMBIGUOUS",sample))
            check_finished_attempt(success[[1L]],sample)
            rec <- list(sample=sample,attempt=success[[1L]],tasks=6L,
                        manifest_sha256=sha256(file.path(
                            success[[1L]],"sample_manifest.json")))
            state$completed_samples[[length(state$completed_samples)+1L]] <- rec
            done <- c(done,sample)
            save_json(state,statusfile)
            cat(sprintf("E5B_BS_PROGRESS completed=%d/36\n",length(done)*6L))
        }
        require(length(done)==6L,"E5B_BS_SIX_SAMPLE_BATCH_INCOMPLETE")
        state$status <- "completed"
        state$finished_utc <- stamp()
        save_json(state,statusfile)
        cat(sprintf(
            "E5B_BS_FINAL status=completed completed=36/36 failed=0 result=%s\n",
            statusfile))
        cat("NO_REFERENCE_LABELS_NO_ARI_NMI\n")
    },error=function(e) {
        state$status <<- "halted"
        state$failures[[length(state$failures)+1L]] <<-
            list(message=conditionMessage(e),when=stamp())
        save_json(state,statusfile)
        cat(sprintf("E5B_BS_HALTED completed=%d/36 error=%s result=%s\n",
                    length(done)*6L,conditionMessage(e),statusfile),
            file=stderr())
        stop(e)
    })
}

if (length(args)==1L && identical(args[[1L]],"--run")) {
    execute()
} else if (length(args)==2L && identical(args[[1L]],"--resume")) {
    execute(normalizePath(args[[2L]],winslash="/",mustWork=TRUE))
} else {
    require(args[[2L]] %in% samples,"E5B_BS_INVALID_CHILD_SAMPLE")
    require(dir.exists(args[[3L]]),"E5B_BS_CHILD_SESSION_MISSING")
    stage <- load_stage()
    run_sample(args[[2L]],args[[3L]],stage)
}
