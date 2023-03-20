using System;
using System.Collections.Generic;
using System.Configuration;
using System.Data;
using System.Linq;
using System.Security.Cryptography;
using System.Threading.Tasks;
using System.Windows;

namespace RIPC_Scanner
{
    /// <summary>
    /// Логика взаимодействия для App.xaml
    /// </summary>
    public partial class App : Application
    {
        public string[] Parameters { get; private set; }
        protected override void OnStartup(StartupEventArgs e)
        {
            setInitParams(e.Args);
            base.OnStartup(e);
        }

        private void setInitParams(string[] args)
        {
            // Проверка получения параметров
            if (args.Length == 0) {
                MessageBox.Show("Запуск возможен только через сайт RIPC!", "Ошибка!", MessageBoxButton.OK, MessageBoxImage.Error, MessageBoxResult.Yes);
                Environment.Exit(0);
                return;
            }
            // Запись параметров в массив
            Parameters = new Uri(args[0].ToString()).AbsolutePath.Split('/').Skip(1).ToArray();
        }

    }
}
