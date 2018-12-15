<?php
echo "<pre>";
system("pwd");
system("whoami");
if (file_exists("build.lock")) {
        echo "Fail. Already in building. ".file_get_contents("build.lock");
        http_response_code(400);
        exit;
}
$d = date("Ymd_His");
file_put_contents("build.lock", "locked at $d");

exec("git rev-parse --abbrev-ref HEAD 2>&1", $cur_branch);
$cur_branch = implode("", $cur_branch);
echo "Current branch: ".$cur_branch."\r\n";

$output_git_pull = "";
exec("git pull 2>&1", $output_git_pull);

$output_build = "";
exec("cd ../../ && ./build-html.py 2>&1", $output_build);

$log = "PHP-Input: ".$php_input."\r\n".
    "Time: ".$d."\r\n\r\n"
        ."$ git pull\r\n".implode("\r\n", $output_git_pull)
        ."\r\n$ ./build.sh\r\n".implode("\r\n", $output_build)."\r\n";

file_put_contents("webhook".$d.".txt", $log);
file_put_contents("last_log.txt", $log);

unlink("build.lock");
echo "Done.\r\n";
