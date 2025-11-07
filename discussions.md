# Lab 9 Notes
This lab demonstrates a multi-service Kubernetes pipeline for an ML system with:
- A trainer CronJob for continuous model retraining
- A backend inference service to serve predictions
- A load balancer service to distribute inference requests
- Shared persistent storage (PVC) for model exchange between trainer and backend

## All deployments, pods, services, and jobs
```
PS C:\Users\STUDENT\Documents\Fall2025\MLinProd\mlip-kubernetes-lab-fall25> kubectl get all
NAME                                            READY   STATUS      RESTARTS   AGE
pod/flask-backend-deployment-6d4bdff9cf-2rq2b   1/1     Running     0          55s
pod/flask-backend-deployment-6d4bdff9cf-tcm7m   1/1     Running     0          54s
pod/flask-load-balancer-fd995d9c8-lp552         1/1     Running     0          25m
pod/model-trainer-job-29375386-s4q9t            0/1     Completed   0          9m38s
pod/model-trainer-job-29375388-9th4b            0/1     Completed   0          7m38s
pod/model-trainer-job-29375390-4cm4x            0/1     Completed   0          5m38s
pod/model-trainer-job-29375392-l49xg            0/1     Completed   0          3m38s
pod/model-trainer-job-29375394-9wn8r            0/1     Completed   0          98s

NAME                                  TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)          AGE
service/flask-backend-service         ClusterIP   10.100.88.95   <none>        5001/TCP         35m
service/flask-load-balancer-service   NodePort    10.98.181.83   <none>        8080:30080/TCP   25m
service/kubernetes                    ClusterIP   10.96.0.1      <none>        443/TCP          6h20m

NAME                                       READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/flask-backend-deployment   2/2     2            2           35m
deployment.apps/flask-load-balancer        1/1     1            1           25m

NAME                                                  DESIRED   CURRENT   READY   AGE
replicaset.apps/flask-backend-deployment-6d4bdff9cf   2         2         2       55s
replicaset.apps/flask-backend-deployment-76bdfc46dc   0         0         0       35m
replicaset.apps/flask-load-balancer-fd995d9c8         1         1         1       25m

NAME                              SCHEDULE      TIMEZONE   SUSPEND   ACTIVE   LAST SCHEDULE   AGE
cronjob.batch/model-trainer-job   */2 * * * *   <none>     False     0        98s             6h6m

NAME                                   STATUS     COMPLETIONS   DURATION   AGE
job.batch/model-trainer-job-29375386   Complete   1/1           5s         9m38s
job.batch/model-trainer-job-29375388   Complete   1/1           5s         7m38s
job.batch/model-trainer-job-29375390   Complete   1/1           4s         5m38s
job.batch/model-trainer-job-29375392   Complete   1/1           5s         3m38s
job.batch/model-trainer-job-29375394   Complete   1/1           5s         98s
PS C:\Users\STUDENT\Documents\Fall2025\MLinProd\mlip-kubernetes-lab-fall25>
```

### Pods
1. two backend inference pods (replicas = 2).
2. flask-load-balancer
3. model-trainer-job-*: automatically created CronJob pods that retrain the model. runs once, trains the model, and finishes with `STATUS: Completed`.

The system has active backend and load balancer services running continuously, while the model trainer runs periodically as separate jobs.

### Services
1. flask-backend-service (ClusterIP): internal service used by the load balancer to reach backend pods inside the cluster (http://flask-backend-service:5001).
2. flask-load-balancer-service (NodePort) — External entry point for users. It exposes port 8080 inside the cluster as 30080 on the Minikube host.

Traffic from outside (Postman, curl) enters via port 30080 → load balancer → backend pods → model predictions.

### Deployments and ReplicaSets
1. Deployments ensure desired replicas are always running.
    - Backend: 2 replicas (for load balancing)
    - Load balancer: 1 replica (single entry point)
2. ReplicaSets are managed by Deployments and track the specific pod versions. The old ReplicaSet (76bdfc46dc) has 0 pods — replaced by the new one (6d4bdff9cf) during rollout.

Shows that backend scaling and updates are managed properly using Deployment/ReplicaSet controllers.

### CronJob and Jobs
1. CronJob (model-trainer-job) is configured to run every 2 minutes (*/2 * * * *).
    - SUSPEND: False, it’s active.
    - ACTIVE: 0, no job currently running.
    - LAST SCHEDULE: 98s, last job triggered recently.

2. Jobs: Each is a completed run of the CronJob.
    - Complete 1/1, finished successfully.
    - Multiple jobs show a consistent 2-minute schedule (9m, 7m, 5m, 3m, 1.5m ago).

Demonstrates continuous retraining of the model at the expected interval and successful job completions.

## How can this be used for milestone 3
1. Containerization of services with a load balancer and deployment replicas fo zero downtime version switching.
2. CronJob for periodic retraining.
3. Load balancer can also be used to route traffic to different backend versions and compare metrics.