import { Command as OCCommand } from "@oclif/command";
import chalk from "chalk";

export abstract class Command extends OCCommand {
  log(message?: string, ...args: any[]) {
    super.log(chalk`{bgGrey  LOG } {grey ${message}}`, ...args);
  }

  warn(input: string | Error) {
    if (typeof input === "string") {
      super.warn(chalk.yellow(input));
      return;
    }
    super.warn(chalk`{bgYellow  WRN } {yellow ${input.name}}`);
    super.warn(chalk.yellow(input.message));
    if (input.stack) {
      super.warn(chalk.dim(input.stack));
    }
  }
}
