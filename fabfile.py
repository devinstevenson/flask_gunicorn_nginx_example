from fabric.api import env, run, settings, sudo, put, cd

env.use_ssh_config = True

def setup():
    with settings(warn_only=True):
        make_nginx_conf()
        run("mkdir -p /home/amd1/github/flaskap")
        put("flaskapp", "/home/amd1/github")
        put("requirements.txt", "/home/amd1/github/flaskapp/requirements.txt")
        with cd("/home/amd1/github/flaskapp"):
            run("/home/amd1/miniconda2/bin/pip install -r requirements.txt")

        put("flaskapp.conf", "/etc/init/flaskapp.conf", use_sudo=True)
        put("flaskapp_nginx", "/etc/nginx/sites-available/flaskapp_nginx", use_sudo=True)

        sudo("rm -rf /etc/nginx/sites-enabled/default")
        sudo("ln -s /etc/nginx/sites-available/flaskapp_nginx /etc/nginx/sites-enabled")
        sudo("start flaskapp")
        run("ps aux | grep flaskapp")
        sudo("service nginx restart")

def cleanup():
    with settings(warn_only=True):
        sudo("stop flaskapp")
        run("rm -rf /home/amd1/github/flaskapp")
        sudo("rm -rf /etc/init/flaskapp.conf")
        sudo("rm -rf /etc/nginx/sites-enabled/flaskapp_nginx")
        sudo("rm -rf /etc/nginx/sites-available/flaskapp_nginx")
        sudo("ln -s /etc/nginx/sites-available/default /etc/nginx/sites-enabled")
        sudo("service nginx restart")
        run("ps aux | grep flaskapp")

def make_nginx_conf():
    conf = ['server {',
            '    listen 80;',
            '    server_name {0};'.format(env['host']),
            '',
            '    location / {',
            '       include    proxy_params;',
            '       proxy_pass http://unix:/home/amd1/github/flaskapp/flaskapp.sock;',
            '    }',
            '}']
    with open('flaskapp_nginx', 'wb') as f:
        for i in conf:
            f.write(i)
            f.write('\n')
