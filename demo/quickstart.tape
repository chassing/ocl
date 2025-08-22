Output quickstart.gif

Set FontSize 20
Set Width 1600
Set Height 600

Type "# Let's run ocl in interactive mode"
Sleep 1s
Enter

Type "ocl"
Sleep 1s
Enter
Sleep 3s
Type@500ms glitchtip
Sleep 3s
Enter
Sleep 5s

Type "# New shell has been spawned with KUBECONFIG, OCL_CLUSTER_NAME, and OCL_CLUSTER_CONSOLE env vars set"
Sleep 3s
Enter

Type "env | grep 'OCL_C\|KUBE'"
Sleep 1s
Enter
Sleep 3s

Type "oc cluster-info"
Sleep 1s
Enter
Sleep 3s

Enter
Ctrl+D
Sleep 1s
Enter

# End
Sleep 5s
