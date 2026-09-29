# Industry and DDN terminology: editorial sources

Reviewed September 28, 2026. These references support the concise glossary in `industry.py`. Definitions are paraphrased; examples are illustrative. Stage associations indicate useful context, not additional sales-stage requirements. Product entries deliberately omit version-specific performance claims.

| Key | Reference and scope |
| --- | --- |
| user | The user's supplied GTM meaning of off-taker: a buyer of GPU capacity or services from a NeoCloud or NCP. This is the AI infrastructure context, not a universal definition across energy and commodity markets. |
| neocloud | [Microsoft: What is a neocloud?](https://www.microsoft.com/en-us/startups/what-is-a-neocloud) — GPU-focused cloud providers. |
| ncp | [NVIDIA Cloud Partners](https://www.nvidia.com/en-us/data-center/gpu-cloud-computing/partners/) — NCP designation and reference designs. |
| cloud | [IBM: Cloud computing](https://www.ibm.com/think/topics/cloud-computing) — cloud service providers and large cloud platforms. |
| factory-ddn | [DDN: AI factories](https://www.ddn.com/solutions/ai-factories/) — GPU services and shared infrastructure. |
| tenancy | [NVIDIA NCP software reference guide: terms](https://docs.nvidia.com/ncx/ncp-software-reference-guide/latest/introduction.html) — tenants and shared infrastructure; [NVIDIA storage certification](https://docs.nvidia.com/certification-programs/certified-storage/latest/nvidia-certified-storage.html) — isolation and quality of service. |
| factory | [NVIDIA: AI factory](https://www.nvidia.com/en-us/glossary/ai-factory/) — integrated infrastructure, enterprise and sovereign uses. |
| hpc | [IBM: Technology topics](https://www.ibm.com/think/topics) — high-performance computing. |
| gpu | [IBM: GPU](https://www.ibm.com/think/topics/gpu) — parallel processing and accelerated workloads. |
| utilization | [NVIDIA NVML utilization metric](https://docs.nvidia.com/deploy/archive/R550/nvml-api/structnvmlUtilization__t.html) and [DCGM profiling metrics](https://docs.nvidia.com/datacenter/dcgm/latest/learn/modules/profiling.html) — GPU activity, memory activity and occupancy are distinct measures. |
| training | [NVIDIA: AI training](https://www.nvidia.com/en-eu/glossary/ai-training/) — training, adaptation and training time. |
| inference | [NVIDIA: AI inference](https://www.nvidia.com/en-us/glossary/ai-inference/) — model execution, tokens and response performance. |
| rag | [NVIDIA: Retrieval-augmented generation](https://www.nvidia.com/en-sg/glossary/retrieval-augmented-generation/) — retrieval and model context. |
| economics | [NVIDIA: Inference economics](https://blogs.nvidia.com/blog/revenue-potential-ai-factories/) — token throughput and delivery economics. |
| checkpoint | [NVIDIA NeMo: Distributed checkpoints](https://docs.nvidia.com/nemo-framework/user-guide/25.04/nemotoolkit/checkpoints/dist_ckpt.html) — saved training state and recovery. |
| platform | [DDN Data Intelligence Platform](https://www.ddn.com/products/data-intelligence-platform/) — EXAScaler, Infinia and data workflows. |
| exascaler | [DDN EXAScaler](https://www.ddn.com/products/lustre-file-system-exascaler/) — parallel file access for AI and HPC. |
| infinia | [DDN Infinia](https://www.ddn.com/products/infinia/) and [Infinia whitepaper overview](https://www.ddn.com/resources/whitepapers/infinia-whitepaper/) — software-defined architecture, metadata and AI workflows. |
| lustre | [DDN EXAScaler technical training overview](https://www.ddn.com/wp-content/uploads/2024/09/DDN-Exascaler-Course-Description.pdf) — open-source Lustre and EXAScaler. |
| storage | [AWS storage decision guide](https://docs.aws.amazon.com/pdfs/decision-guides/latest/storage-on-aws-how-to-choose/storage-on-aws-how-to-choose.pdf) and [Amazon S3 FAQs](https://aws.amazon.com/s3/faqs/) — storage access and performance terminology. |
| certification | [NVIDIA-Certified Storage](https://docs.nvidia.com/certification-programs/certified-storage/latest/nvidia-certified-storage.html) — certification scope and data-path performance. |
| editorial | General explanatory definitions, measurement conventions and arithmetic examples written for this glossary. These are not DDN pricing, policy, contractual commitments or approved reporting metrics. |

“GPU capacity occupancy” is explicitly a commercial measure in this glossary; it must not be confused with CUDA streaming-multiprocessor occupancy. NCP uses NVIDIA's current public expansion, NVIDIA Cloud Partner. “NVIDIA cloud provider” is retained as a search alias for familiar wording.
